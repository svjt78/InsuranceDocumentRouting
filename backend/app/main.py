# backend/app/main.py

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import uuid
import json
import os
import logging
import traceback
import boto3
from botocore.exceptions import ClientError

from .logging_config import setup_logging
from . import models, database
from .rabbitmq import publish_message
from .bucket_mappings import router as bucket_mappings_router
from .email_settings import router as email_settings_router
from .routes.doc_hierarchy import router as doc_hierarchy_router
from .seed_data.seed_hierarchy import run_seed
from .metrics.router import router as metrics_router
from .destination_service import process_document_destination  # 🆕 import routing logic

# ───────────────────────────────────────── setup ───────────────────────────────────────────
setup_logging()
logger = logging.getLogger("main")

app = FastAPI(
    title="Insurance Document API",
    description=(
        "Handles uploads, OCR, classification of insurance documents, "
        "bucket mapping, email settings, and ingestion mode."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ───────────────────────────────────────── MinIO ────────────────────────────────────────────
s3_client = boto3.client(
    "s3",
    endpoint_url=os.getenv("MINIO_ENDPOINT"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)
BUCKET = os.getenv("MINIO_BUCKET", "documents")

# simple in-memory toggle
_ingestion_mode = os.getenv("INGESTION_MODE", "realtime")

# ───────────────────────────────────────── DB dep ───────────────────────────────────────────
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ───────────────────────────────────────── startup ─────────────────────────────────────────
@app.on_event("startup")
def startup() -> None:
    logger.info("Starting up application…")

    # Auto-seed doc_hierarchy
    with database.engine.begin() as conn:
        cnt = conn.execute(text("SELECT COUNT(*) FROM doc_hierarchy")).scalar()
        if cnt == 0:
            logger.info("doc_hierarchy empty – seeding initial hierarchy")
            run_seed()
        else:
            logger.info("doc_hierarchy already populated (%s rows)", cnt)

    # Ensure MinIO bucket exists
    try:
        s3_client.head_bucket(Bucket=BUCKET)
        logger.info("MinIO bucket '%s' exists.", BUCKET)
    except ClientError as e:
        code = e.response["Error"].get("Code", "")
        if code in ("404", "403", "NoSuchBucket", "AccessDenied"):
            s3_client.create_bucket(Bucket=BUCKET)
            logger.info("MinIO bucket '%s' created.", BUCKET)
        else:
            logger.exception("Error checking/creating MinIO bucket: %s", e)
            raise

# ───────────────────────────────────────── API – upload ──────────────────────────────────────
@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    logger.info("Received upload: %s", file.filename)
    file_id = str(uuid.uuid4())
    s3_key = f"{file_id}_{file.filename}"
    tmp_path = f"/tmp/{s3_key}"

    # local temp write
    content = await file.read()
    try:
        with open(tmp_path, "wb") as f:
            f.write(content)
    except Exception as e:
        logger.exception("Local write failed: %s", e)
        raise HTTPException(status_code=500, detail="File write error")

    # MinIO upload
    try:
        s3_client.upload_file(tmp_path, BUCKET, s3_key)
    except Exception as e:
        logger.exception("MinIO upload failed: %s", e)
        raise HTTPException(status_code=500, detail="MinIO upload failed")

    # DB record
    try:
        doc = models.Document(filename=file.filename, s3_key=s3_key, status="Pending")
        db.add(doc)
        db.commit()
        db.refresh(doc)
    except Exception as e:
        db.rollback()
        logger.exception("DB insert failed: %s", e)
        raise HTTPException(status_code=500, detail="Database insert failed")

    # RabbitMQ notify
    try:
        publish_message("document_queue", json.dumps({"doc_id": doc.id, "s3_key": s3_key}))
    except Exception as e:
        logger.exception("RabbitMQ publish failed: %s", e)
        raise HTTPException(status_code=500, detail="RabbitMQ publish failed")

    return {"message": "Uploaded successfully", "document_id": doc.id}

# ───────────────────────────────────────── API – queries ─────────────────────────────────────
@app.get("/documents")
def get_documents(db: Session = Depends(get_db)):
    docs = db.query(models.Document).all()
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "department": d.department,
            "category": d.category,
            "subcategory": d.subcategory,
            "summary": d.summary,
            "action_items": d.action_items,
            "status": d.status,
            "updated_at": d.updated_at,
            "created_at": d.created_at,
            "destination_bucket": d.destination_bucket,
            "destination_key": d.destination_key,
        }
        for d in docs
    ]

@app.get("/document/{doc_id}")
def get_document(doc_id: int, db: Session = Depends(get_db)):
    d = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not d:
        logger.warning("Document not found: %s", doc_id)
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "id": d.id,
        "filename": d.filename,
        "s3_key": d.s3_key,
        "extracted_text": d.extracted_text,
        "department": d.department,
        "category": d.category,
        "subcategory": d.subcategory,
        "summary": d.summary,
        "action_items": d.action_items,
        "status": d.status,
        "updated_at": d.updated_at,
        "created_at": d.created_at,
        "destination_bucket": d.destination_bucket,
        "destination_key": d.destination_key,
    }

# ─────────────────────────────────────── API – override (now synchronous) ───────────────────────────────────
@app.post("/document/{doc_id}/override")
def override_document(
    doc_id: int,
    override: dict = Body(...),
    db: Session = Depends(get_db),
):
    logger.info(f"=== OVERRIDE START doc_id={doc_id} ===")
    from .models import Document

    d = db.query(Document).get(doc_id)
    if not d:
        logger.warning(f"Document {doc_id} not found for override")
        raise HTTPException(status_code=404, detail="Document not found")

    # Track which fields actually change
    orig = {
        "department": d.department,
        "category": d.category,
        "subcategory": d.subcategory,
        "summary": d.summary,
        "action_items": d.action_items,
    }
    classification_changed = False
    for field in ("department", "category", "subcategory", "summary", "action_items"):
        if override.get(field) is not None and override[field] != getattr(d, field):
            setattr(d, field, override[field])
            classification_changed = True
            logger.info(f"Overriding {field}: {orig[field]!r} -> {override[field]!r}")

    if not classification_changed:
        logger.info("No fields changed—no commit")
        return {
            "id": d.id,
            "department": d.department,
            "category": d.category,
            "subcategory": d.subcategory,
            "summary": d.summary,
            "action_items": d.action_items,
            "status": d.status,
            "destination_bucket": d.destination_bucket,
            "destination_key": d.destination_key,
        }

    # Commit override changes
    d.status = "Processed with Override"
    try:
        db.commit()
        db.refresh(d)
    except Exception as e:
        db.rollback()
        logger.exception("Override commit failed")
        raise HTTPException(status_code=500, detail=f"Override commit error: {e}")

    # Immediately re-route based on new classification
    logger.info(f"Running synchronous reroute for doc_id={doc_id}")
    success, error_msg, new_bucket, new_key = process_document_destination(
        d, db, s3_client, BUCKET
    )
    d.destination_bucket = new_bucket
    d.destination_key    = new_key
    d.error_message      = error_msg
    d.status             = (
        "Processed with Override" if success
        else ("No Destination" if error_msg and error_msg.startswith("No matching") else "Failed")
    )
    try:
        db.commit()
        db.refresh(d)
        logger.info(f"Inline reroute completed: bucket={new_bucket} key={new_key}")
    except Exception as e:
        db.rollback()
        logger.exception("Reroute commit failed")
        raise HTTPException(status_code=500, detail=f"Reroute commit error: {e}")

    logger.info(f"=== OVERRIDE END doc_id={doc_id} ===")
    return {
        "id": d.id,
        "department": d.department,
        "category": d.category,
        "subcategory": d.subcategory,
        "summary": d.summary,
        "action_items": d.action_items,
        "status": d.status,
        "destination_bucket": d.destination_bucket,
        "destination_key": d.destination_key,
        "error_message": d.error_message,
    }

# ────────────────────────────────────── soft-delete ─────────────────────────────────────────
@app.delete("/document/{doc_id}", status_code=204)
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    d = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(d)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.exception("Delete failed: %s", e)
        raise HTTPException(status_code=500, detail="Delete failed")

# ───────────────────────────────── ingestion-mode endpoints ─────────────────────────────────
from pydantic import BaseModel

class IngestionModePayload(BaseModel):
    mode: str  # "realtime" or "batch"

@app.get("/ingestion-mode")
def get_ingestion_mode():
    return {"mode": _ingestion_mode}

@app.put("/ingestion-mode")
def set_ingestion_mode(payload: IngestionModePayload):
    global _ingestion_mode
    if payload.mode not in ("realtime", "batch"):
        raise HTTPException(status_code=400, detail="Invalid mode")
    _ingestion_mode = payload.mode
    logger.info("Ingestion mode set to: %s", _ingestion_mode)
    return {"mode": _ingestion_mode}

# ───────────────────────────────── include routers ──────────────────────────────────────────
app.include_router(bucket_mappings_router, prefix="/bucket-mappings", tags=["Bucket Mappings"])
app.include_router(email_settings_router, prefix="/email-settings", tags=["Email Settings"])
app.include_router(doc_hierarchy_router, prefix="/lookup", tags=["Lookup"])
app.include_router(metrics_router)
