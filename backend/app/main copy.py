from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uuid
import json
import boto3
import os
from botocore.exceptions import ClientError

from . import models, database
from .rabbitmq import publish_message

app = FastAPI()

# Enable CORS (adjust allowed origins as necessary)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load config from environment
MINIO_URL = os.getenv("MINIO_ENDPOINT")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET = os.getenv("MINIO_BUCKET", "documents")

# Initialize MinIO S3 client using boto3
s3_client = boto3.client(
    's3',
    endpoint_url=MINIO_URL,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

# Dependency for DB sessions
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup():
    # Create database tables if not present
    models.Base.metadata.create_all(bind=database.engine)

    # Ensure MinIO bucket exists or create it
    try:
        s3_client.head_bucket(Bucket=BUCKET)
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code in ["404", "403", "NoSuchBucket", "AccessDenied"]:
            s3_client.create_bucket(Bucket=BUCKET)
        else:
            raise e

@app.post("/upload")
async def upload_document(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    file_id = str(uuid.uuid4())
    file_location = f"/tmp/{file_id}_{file.filename}"
    with open(file_location, "wb") as f:
        content = await file.read()
        f.write(content)

    s3_key = f"{file_id}_{file.filename}"
    try:
        s3_client.upload_file(file_location, BUCKET, s3_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MinIO upload failed: {e}")

    # Create a Document record in the DB
    db = next(get_db())
    document = models.Document(filename=file.filename, s3_key=s3_key, status='pending')
    db.add(document)
    db.commit()
    db.refresh(document)

    # Publish processing message to RabbitMQ
    message = {
        "doc_id": document.id,
        "s3_key": s3_key
    }
    publish_message("document_queue", json.dumps(message))

    return {"message": "File uploaded successfully", "document_id": document.id}

@app.get("/documents")
def get_documents():
    db = next(get_db())
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
def get_document(doc_id: int):
    db = next(get_db())
    document = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not document:
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
def override_document(doc_id: int, override: dict):
    db = next(get_db())
    document = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    document.department = override.get("department", document.department)
    document.category = override.get("category", document.category)
    document.subcategory = override.get("subcategory", document.subcategory)
    document.summary = override.get("summary", document.summary)
    document.action_items = override.get("action_items", document.action_items)
    document.status = "overridden"
    db.commit()
    return {"message": "Document classification overridden", "document_id": doc_id}
