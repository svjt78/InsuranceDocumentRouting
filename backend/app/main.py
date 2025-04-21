# backend/app/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text             # 🆕  used for quick row‑count
import uuid, json, os, logging, boto3
from botocore.exceptions import ClientError

from .logging_config import setup_logging
from . import models, database
from .rabbitmq import publish_message
from .bucket_mappings import router as bucket_mappings_router
from .email_settings import router as email_settings_router
from .routes.doc_hierarchy import router as doc_hierarchy_router
from .seed_data.seed_hierarchy import run_seed            # 🆕  auto‑seed helper
from .config import (
    DATABASE_URL,
    RABBITMQ_URL,
    MINIO_ENDPOINT,
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
)

# ─────────────────────────────────────────  setup  ─────────────────────────────────────────
setup_logging()
logger = logging.getLogger("main")

app = FastAPI(
    title="Insurance Document API",
    description="Handles uploads, OCR, classification of insurance documents, bucket mapping, "
                "email settings, and ingestion mode.",
)

app.add_middleware(
    CORSMiddleware,
    #allow_origins=["http://localhost:3001"],
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ────────────────────────────────────────  MinIO  ──────────────────────────────────────────
s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)
BUCKET = os.getenv("MINIO_BUCKET", "documents")

# simple in‑memory toggle (could live in DB later)
_ingestion_mode = os.getenv("INGESTION_MODE", "realtime")

# ────────────────────────────────────────  DB dep  ─────────────────────────────────────────
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ───────────────────────────────────────  startup  ─────────────────────────────────────────
@app.on_event("startup")
def startup() -> None:
    logger.info("Starting up application…")

    # 1) (optional) create tables if you don’t run Alembic separately
    # models.Base.metadata.create_all(bind=database.engine)

    # 2) Auto‑seed doc_hierarchy once
    with database.engine.begin() as conn:
        cnt = conn.execute(text("SELECT COUNT(*) FROM doc_hierarchy")).scalar()
        if cnt == 0:
            logger.info("doc_hierarchy empty – seeding initial hierarchy")
            run_seed()
        else:
            logger.info("doc_hierarchy already populated (%s rows)", cnt)

    # 3) Ensure MinIO bucket exists
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

# ─────────────────────────────────────  API – upload  ──────────────────────────────────────
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
        doc = models.Document(filename=file.filename, s3_key=s3_key, status="pending")
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

# ─────────────────────────────────────  API – queries  ──────────────────────────────────────
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

# ─────────────────────────────────────  API – override  ─────────────────────────────────────
@app.post("/document/{doc_id}/override")
def override_document(doc_id: int, override: dict, db: Session = Depends(get_db)):
    d = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not d:
        logger.warning("Override target not found: %s", doc_id)
        raise HTTPException(status_code=404, detail="Document not found")

    for field in ("department", "category", "subcategory", "summary", "action_items"):
        if override.get(field) is not None:
            setattr(d, field, override[field])
    d.status = "overridden"

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.exception("Override commit failed: %s", e)
        raise HTTPException(status_code=500, detail="Override failed")

    return {"message": "Override saved", "document_id": doc_id}

# soft‑delete
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

# ─────────────────────────────────  ingestion‑mode endpoints  ───────────────────────────────
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

# ─────────────────────────────  include feature routers  ───────────────────────────────────
app.include_router(bucket_mappings_router, prefix="/bucket-mappings", tags=["Bucket Mappings"])
app.include_router(email_settings_router,  prefix="/email-settings",    tags=["Email Settings"])
app.include_router(doc_hierarchy_router,   prefix="/lookup",            tags=["Lookup"])
