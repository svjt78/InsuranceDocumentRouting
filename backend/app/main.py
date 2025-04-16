from .logging_config import setup_logging

# Initialize logging before anything else
setup_logging()

import logging
from typing import Optional  # kept in case you need it elsewhere

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

# Routers
from .bucket_mappings import router as bucket_mappings_router
from . import email_settings

# ---- hierarchy seeder ----
from .seed_data.seed_hierarchy import run_seed
# --------------------------

from .routes import doc_hierarchy as doc_hierarchy_router

# Setup logging (extra safeguard)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

app = FastAPI(
    title="Insurance Document API",
    description=(
        "Handles uploads, OCR, classification of insurance documents, and "
        "MinIO bucket mapping management."
    ),
)

# Enable CORS
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

# MinIO client
s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_URL,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)

# DB session dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def startup() -> None:
    """Ensure tables, seed hierarchy, check MinIO bucket."""
    logger.info("Starting up application…")

    # Tables
    models.Base.metadata.create_all(bind=database.engine)
    logger.info("Database tables ensured (including doc_hierarchy).")

    # Seed hierarchy (idempotent)
    run_seed()

    # Bucket
    try:
        s3_client.head_bucket(Bucket=BUCKET)
        logger.info("MinIO bucket '%s' already exists.", BUCKET)
    except ClientError as e:
        if e.response["Error"].get("Code", "") in (
            "404",
            "403",
            "NoSuchBucket",
            "AccessDenied",
        ):
            s3_client.create_bucket(Bucket=BUCKET)
            logger.info("MinIO bucket '%s' created.", BUCKET)
        else:
            logger.exception("MinIO error on bucket check: %s", e)
            raise


# Routers
app.include_router(bucket_mappings_router, prefix="/bucket-mappings", tags=["Bucket Mappings"])
app.include_router(email_settings.router, prefix="/email-settings", tags=["Email Settings"])
app.include_router(doc_hierarchy_router.router, prefix="/lookup", tags=["Lookup"])


# ---------- Document APIs ----------
@app.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,  # BackgroundTasks must come first
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    logger.info("Received file upload request: %s", file.filename)

    file_id = str(uuid.uuid4())
    file_location = f"/tmp/{file_id}_{file.filename}"
    s3_key = f"{file_id}_{file.filename}"

    # Save locally
    try:
        content = await file.read()
        with open(file_location, "wb") as f:
            f.write(content)
        logger.info("File saved locally at: %s", file_location)
    except Exception as e:
        logger.exception("Failed to save file locally: %s", e)
        raise HTTPException(status_code=500, detail="File write error")

    # Upload to MinIO
    try:
        s3_client.upload_file(file_location, BUCKET, s3_key)
        logger.info("File uploaded to MinIO: %s", s3_key)
    except Exception as e:
        logger.exception("Failed to upload to MinIO: %s", e)
        raise HTTPException(status_code=500, detail="MinIO upload failed")

    # Insert DB record
    try:
        document = models.Document(filename=file.filename, s3_key=s3_key, status="pending")
        db.add(document)
        db.commit()
        db.refresh(document)
        logger.info("Inserted document into DB with ID: %s", document.id)
    except Exception as e:
        db.rollback()
        logger.exception("Failed to commit to DB: %s", e)
        raise HTTPException(status_code=500, detail="Database insert failed")

    # Publish message to RabbitMQ
    try:
        message = json.dumps({"doc_id": document.id, "s3_key": s3_key})
        publish_message("document_queue", message)
        logger.info("Published message to RabbitMQ for document ID: %s", document.id)
    except Exception as e:
        logger.exception("Failed to publish message to RabbitMQ: %s", e)
        raise HTTPException(status_code=500, detail="RabbitMQ publish failed")

    return {"message": "File uploaded successfully", "document_id": document.id}


@app.get("/documents")
def get_documents(db: Session = Depends(get_db)):
    logger.info("Fetching all documents from DB…")
    documents = db.query(models.Document).all()
    return [
        {
            "id": doc.id,
            "filename": doc.filename,
            "department": doc.department,
            "category": doc.category,
            "subcategory": doc.subcategory,
            "summary": doc.summary,
            "action_items": doc.action_items,
            "status": doc.status,
        }
        for doc in documents
    ]


@app.get("/document/{doc_id}")
def get_document(doc_id: int, db: Session = Depends(get_db)):
    logger.info("Fetching document with ID: %s", doc_id)
    document = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not document:
        logger.warning("Document not found: %s", doc_id)
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
        "status": document.status,
    }


@app.post("/document/{doc_id}/override")
def override_document(doc_id: int, override: dict, db: Session = Depends(get_db)):
    logger.info("Overriding document with ID: %s", doc_id)
    document = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not document:
        logger.warning("Document not found for override: %s", doc_id)
        raise HTTPException(status_code=404, detail="Document not found")

    document.department = override.get("department", document.department)
    document.category = override.get("category", document.category)
    document.subcategory = override.get("subcategory", document.subcategory)
    document.summary = override.get("summary", document.summary)
    document.action_items = override.get("action_items", document.action_items)
    document.status = "overridden"

    try:
        db.commit()
        logger.info("Document %s overridden and saved.", doc_id)
    except Exception as e:
        db.rollback()
        logger.exception("Failed to override document %s: %s", doc_id, e)
        raise HTTPException(status_code=500, detail="Document override failed")

    return {"message": "Document classification overridden", "document_id": doc_id}
