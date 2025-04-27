# backend/app/main.py

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import uuid, json, os, logging, boto3
from botocore.exceptions import ClientError

from .logging_config import setup_logging
from . import models, database
from .rabbitmq import publish_message
from .bucket_mappings import router as bucket_mappings_router
from .email_settings import router as email_settings_router
from .routes.doc_hierarchy import router as doc_hierarchy_router
from .seed_data.seed_hierarchy import run_seed
from .metrics.router import router as metrics_router
from .config import (
    DATABASE_URL,
    RABBITMQ_URL,
    MINIO_ENDPOINT,
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
)
from .destination_service import process_document_destination  # 🆕 import bucket routing logic

# ───────────────────────────────────────── setup ───────────────────────────────────────────
setup_logging()
logger = logging.getLogger("main")

app = FastAPI(
    title="Insurance Document API",
    description="Handles uploads, OCR, classification of insurance documents, bucket mapping, "
                "email settings, and ingestion mode.",
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
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)
BUCKET = os.getenv("MINIO_BUCKET", "documents")

# simple in‑memory toggle
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

    # Auto‑seed doc_hierarchy
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

# ───────────────────────────────────────── API – upload ─────────────────────────────────────
@app.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    logger.info("Received upload: %s", file.filename)
    file_id  = str(uuid.uuid4())
    s3_key   = f"{file_id}_{file.filename}"
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
        db.add(doc); db.commit(); db.refresh(doc)
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

# ───────────────────────────────────────── API – queries ────────────────────────────────────
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
            "destination_key":    d.destination_key,
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
        "destination_key":    d.destination_key,
    }

# ──────────────────────────────────────── background task ──────────────────────────────────
def _reroute_document(doc_id: int):
    """Background task to copy file to new bucket and update DB."""
    db = database.SessionLocal()
    try:
        doc = db.query(models.Document).get(doc_id)
        if not doc:
            return

        success, error_msg, dest_bucket, dest_key = process_document_destination(
            doc, db, s3_client, BUCKET
        )

        doc.destination_bucket = dest_bucket
        doc.destination_key = dest_key
        doc.error_message = error_msg

        if success:
            doc.status = "Processed with Override"
        else:
            doc.status = "No Destination" if error_msg.startswith("No matching") else "failed"

        db.commit()

    except Exception as e:
        logger.exception("Background reroute failed for doc_id=%s: %s", doc_id, e)
        db.rollback()
    finally:
        db.close()

# ─────────────────────────────────────── API – override ────────────────────────────────────
@app.post("/document/{doc_id}/override")
def override_document(
    doc_id: int,
    override: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    d = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not d:
        logger.warning("Override target not found: %s", doc_id)
        raise HTTPException(status_code=404, detail="Document not found")

    # detect changes
    orig_dept, orig_cat, orig_subcat = d.department, d.category, d.subcategory
    classification_changed = (
        (override.get("department") and override["department"] != orig_dept) or
        (override.get("category")   and override["category"]   != orig_cat) or
        (override.get("subcategory")and override["subcategory"]!= orig_subcat)
    )
    summary_changed = (
        override.get("summary") is not None and override["summary"] != d.summary
    )
    action_changed = (
        override.get("action_items") is not None and override["action_items"] != d.action_items
    )

    # if no field changed, return as-is without touching status
    if not (classification_changed or summary_changed or action_changed):
        return {
            "id": d.id,
            "department": d.department,
            "category": d.category,
            "subcategory": d.subcategory,
            "summary": d.summary,
            "action_items": d.action_items,
            "status": d.status,
            "destination_bucket": d.destination_bucket,
            "destination_key":    d.destination_key,
        }

    # apply overrides
    for field in ("department", "category", "subcategory", "summary", "action_items"):
        if override.get(field) is not None:
            setattr(d, field, override[field])

    # set status
    if classification_changed:
        d.status = "Processed with Override"
    elif summary_changed or action_changed:
        d.status = "Overridden"

    # commit immediate changes
    try:
        db.commit()
        db.refresh(d)
    except Exception as e:
        db.rollback()
        logger.exception("Override commit failed: %s", e)
        raise HTTPException(status_code=500, detail="Override failed")

    # schedule background bucket copy if classification changed
    if classification_changed:
        background_tasks.add_task(_reroute_document, doc_id)

    # return full updated record
    return {
        "id": d.id,
        "department": d.department,
        "category": d.category,
        "subcategory": d.subcategory,
        "summary": d.summary,
        "action_items": d.action_items,
        "status": d.status,
        "destination_bucket": d.destination_bucket,
        "destination_key":    d.destination_key,
    }

# ────────────────────────────────────── soft‑delete ───────────────────────────────────────
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

# ───────────────────────────────────── ingestion‑mode endpoints ───────────────────────────
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
app.include_router(email_settings_router,  prefix="/email-settings",    tags=["Email Settings"])
app.include_router(doc_hierarchy_router,   prefix="/lookup",            tags=["Lookup"])
#app.include_router(metrics_router,  prefix="/metrics", tags=["Metrics"])  
app.include_router(metrics_router)
