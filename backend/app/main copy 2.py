from .logging_config import setup_logging

# Initialize logging before anything else
setup_logging()

import logging
logger = logging.getLogger("main")

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uuid
import json
import boto3
import os
from botocore.exceptions import ClientError

from . import models, database
from .rabbitmq import publish_message

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

app = FastAPI(
    title="Insurance Document API",
    description="Handles uploads, OCR, and classification of insurance documents."
)

# Enable CORS (adjust allowed origins as necessary)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load config from environment
MINIO_URL = os.getenv("MINIO_ENDPOINT")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET = os.getenv("MINIO_BUCKET", "documents")

# Initialize MinIO S3 client
s3_client = boto3.client(
    's3',
    endpoint_url=MINIO_URL,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

# DB session dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup():
    logger.info("Starting up application...")
    try:
        models.Base.metadata.create_all(bind=database.engine)
        logger.info("Database tables ensured.")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise

    try:
        s3_client.head_bucket(Bucket=BUCKET)
        logger.info(f"MinIO bucket '{BUCKET}' already exists.")
    except ClientError as e:
        error_code = e.response['Error'].get('Code', '')
        if error_code in ["404", "403", "NoSuchBucket", "AccessDenied"]:
            try:
                s3_client.create_bucket(Bucket=BUCKET)
                logger.info(f"MinIO bucket '{BUCKET}' created.")
            except Exception as create_exc:
                logger.error(f"Failed to create bucket: {create_exc}")
                raise
        else:
            logger.error(f"MinIO error on bucket check: {e}")
            raise

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    logger.info(f"Received file upload request: {file.filename}")

    file_id = str(uuid.uuid4())
    file_location = f"/tmp/{file_id}_{file.filename}"
    s3_key = f"{file_id}_{file.filename}"

    try:
        content = await file.read()
        with open(file_location, "wb") as f:
            f.write(content)
        logger.info(f"File saved locally at: {file_location}")
    except Exception as e:
        logger.error(f"Failed to save file locally: {e}")
        raise HTTPException(status_code=500, detail="File write error")

    try:
        s3_client.upload_file(file_location, BUCKET, s3_key)
        logger.info(f"File uploaded to MinIO: {s3_key}")
    except Exception as e:
        logger.error(f"Failed to upload to MinIO: {e}")
        raise HTTPException(status_code=500, detail="MinIO upload failed")

    try:
        document = models.Document(filename=file.filename, s3_key=s3_key, status='pending')
        db.add(document)
        db.commit()
        db.refresh(document)
        logger.info(f"Inserted document into DB with ID: {document.id}")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to commit to DB: {e}")
        raise HTTPException(status_code=500, detail="Database insert failed")

    try:
        message = json.dumps({"doc_id": document.id, "s3_key": s3_key})
        publish_message("document_queue", message)
        logger.info(f"Published message to RabbitMQ for document ID: {document.id}")
    except Exception as e:
        logger.error(f"Failed to publish message to RabbitMQ: {e}")
        raise HTTPException(status_code=500, detail="RabbitMQ publish failed")

    return {"message": "File uploaded successfully", "document_id": document.id}

@app.get("/documents")
def get_documents(db: Session = Depends(get_db)):
    logger.info("Fetching all documents from DB...")
    documents = db.query(models.Document).all()
    return [{
        "id": doc.id,
        "filename": doc.filename,
        "department": doc.department,
        "category": doc.category,
        "subcategory": doc.subcategory,
        "summary": doc.summary,
        "action_items": doc.action_items,
        "status": doc.status
    } for doc in documents]

@app.get("/document/{doc_id}")
def get_document(doc_id: int, db: Session = Depends(get_db)):
    logger.info(f"Fetching document with ID: {doc_id}")
    document = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not document:
        logger.warning(f"Document not found: {doc_id}")
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "id": document.id,
        "filename": document.filename,
        "s3_key": document.s3_key,
        "extracted_text": document.extracted_text,
        "department": document.department,
        "category": document.category,
        "subcategory": document.subcategory,
        "summary": document.summary,
        "action_items": document.action_items,
        "status": document.status
    }

@app.post("/document/{doc_id}/override")
def override_document(doc_id: int, override: dict, db: Session = Depends(get_db)):
    logger.info(f"Overriding document with ID: {doc_id}")
    document = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not document:
        logger.warning(f"Document not found for override: {doc_id}")
        raise HTTPException(status_code=404, detail="Document not found")
    
    document.department = override.get("department", document.department)
    document.category = override.get("category", document.category)
    document.subcategory = override.get("subcategory", document.subcategory)
    document.summary = override.get("summary", document.summary)
    document.action_items = override.get("action_items", document.action_items)
    document.status = "overridden"

    try:
        db.commit()
        logger.info(f"Document {doc_id} overridden and saved.")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to override document {doc_id}: {e}")
        raise HTTPException(status_code=500, detail="Document override failed")

    return {"message": "Document classification overridden", "document_id": doc_id}
