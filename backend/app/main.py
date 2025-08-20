# backend/app/main.py

import os
import uuid
import json
import logging

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Body, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import boto3
from botocore.exceptions import ClientError
from sqlalchemy import text

from .logging_config import setup_logging
from . import models, database
from .models import Document1
from .bucket_mappings import router as bucket_mappings_router
from .email_settings import router as email_settings_router
from .routes.doc_hierarchy import router as doc_hierarchy_router
from .seed_data.seed_hierarchy import run_seed
from .metrics.router import router as metrics_router
from .api.account_policy import router as account_policy_router

# New API v1 routers
from .api.v1.accounts import router as accounts_v1_router
from .api.v1.policies import router as policies_v1_router
from .api.v1.claims import router as claims_v1_router
from .api.v1.email_webhook import router as webhook_router
from .s3_client import s3_client

from .destination_service import process_document_destination
from .config import (
    AWS_REGION,
    AWS_S3_BUCKET,
    S3_INPUT_PREFIX,
    OUTBOX_POLL_INTERVAL,
    PRESIGNED_URL_EXPIRES_IN,
)
from .ws_manager import manager  # ← import the WebSocket ConnectionManager

# ───────────────────────────────────────── setup ───────────────────────────────────────────
setup_logging()
logger = logging.getLogger("main")

# ───────────────────────────────────────── AWS S3 ────────────────────────────────────────────
if not AWS_S3_BUCKET:
    logger.error("Missing AWS_S3_BUCKET environment variable")
    raise RuntimeError("AWS_S3_BUCKET must be set")

#s3_client = boto3.client(
#    "s3",
#    region_name=AWS_REGION,
#    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
#    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
#)

# simple in-memory toggle
_ingestion_mode = os.getenv("INGESTION_MODE", "realtime")

# ───────────────────────────────────────── DB dep ───────────────────────────────────────────
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

    # # Verify AWS S3 bucket exists
    # try:
    #     s3_client.head_bucket(Bucket=AWS_S3_BUCKET)
    #     logger.info("S3 bucket '%s' accessible.", AWS_S3_BUCKET)
    # except ClientError as e:
    #     logger.exception("Unable to access S3 bucket '%s': %s", AWS_S3_BUCKET, e)
    #     raise RuntimeError(f"Cannot access S3 bucket: {AWS_S3_BUCKET}")

# ───────────────────────────────────────── WebSocket ────────────────────────────────────────
@app.websocket("/ws/accounts")
async def accounts_updates(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            # keep connection alive (no incoming messages expected)
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)

# ───────────────────────────────────────── API – upload ──────────────────────────────────────
@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    logger.info("Received upload: %s", file.filename)
    file_id = str(uuid.uuid4())
    key_name = f"{file_id}_{file.filename}"
    s3_key = f"{S3_INPUT_PREFIX.rstrip('/')}/{key_name}"
    tmp_path = f"/tmp/{key_name}"

    # local temp write
    content = await file.read()
    try:
        with open(tmp_path, "wb") as f:
            f.write(content)
    except Exception as e:
        logger.exception("Local write failed: %s", e)
        raise HTTPException(status_code=500, detail="File write error")

    # AWS S3 upload
    try:
        s3_client.upload_file(tmp_path, AWS_S3_BUCKET, s3_key)
        logger.info("Uploaded to S3: %s/%s", AWS_S3_BUCKET, s3_key)
    except Exception as e:
        logger.exception("S3 upload failed: %s", e)
        # Record failure
        fail_db = database.SessionLocal()
        try:
            fail_doc = models.Document1(
                filename=file.filename,
                s3_key=s3_key,
                status="Failed",
                error_message=str(e),
                account_number="XXXX",
                policyholder_name="XXXX",
                policy_number="XXXX",
                claim_number="XXXX",
            )
            fail_db.add(fail_doc)
            fail_db.commit()
        finally:
            fail_db.close()
        raise HTTPException(status_code=500, detail="S3 upload failed")

    # DB record into Document1
    try:
        doc = models.Document1(
            filename=file.filename,
            s3_key=s3_key,
            status="Pending",
            account_number="XXXX",
            policyholder_name="XXXX",
            policy_number="XXXX",
            claim_number="XXXX",
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
    except Exception as e:
        db.rollback()
        logger.exception("DB insert failed: %s", e)
        raise HTTPException(status_code=500, detail="Database insert failed")

    # Enqueue in outbox
    out_db = database.SessionLocal()
    try:
        out = models.MessageOutbox(
            exchange="",
            routing_key="document_queue",
            payload={"doc_id": doc.id, "s3_key": s3_key},
        )
        out_db.add(out)
        out_db.commit()
        logger.info("Enqueued outbox id=%s", out.id)
    except Exception as e:
        out_db.rollback()
        logger.exception("Outbox write failed: %s", e)
    finally:
        out_db.close()

    # Broadcast WebSocket message to notify clients
    await manager.broadcast({"type": "new_document", "document_id": doc.id})

    return {"message": "Uploaded successfully", "document_id": doc.id}

# ───────────────────────────────── API – list & detail ─────────────────────────────────────
@app.get("/documents")
def get_documents(db: Session = Depends(get_db)):
    docs = (
        db.query(Document1)
          .order_by(Document1.updated_at.desc(), Document1.created_at.desc())
          .all()
    )
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "account_number": d.account_number,
            "policyholder_name": d.policyholder_name,
            "policy_number": d.policy_number,
            "claim_number": d.claim_number,
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
            "error_message": d.error_message,
            "email_error": d.email_error,
        }
        for d in docs
    ]

@app.get("/documents/{doc_id}/download")
def get_download_url(doc_id: int, db: Session = Depends(get_db)):
    d = db.query(models.Document1).filter(models.Document1.id == doc_id).first()
    if not d or not d.destination_key:
        raise HTTPException(status_code=404, detail="Document not found or not yet routed")

    try:
        url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": AWS_S3_BUCKET, "Key": d.destination_key},
            ExpiresIn=PRESIGNED_URL_EXPIRES_IN,
        )
    except ClientError as e:
        logger.exception("Error generating presigned URL: %s", e)
        raise HTTPException(status_code=500, detail="Failed to generate download URL")

    # Redirect the client directly to the S3 presigned URL, triggering the download
    return RedirectResponse(url)

@app.get("/document/{doc_id}")
def get_document(doc_id: int, db: Session = Depends(get_db)):
    d = db.query(models.Document1).filter(models.Document1.id == doc_id).first()
    if not d:
        logger.warning("Document not found: %s", doc_id)
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "id": d.id,
        "filename": d.filename,
        "s3_key": d.s3_key,
        "extracted_text": d.extracted_text,
        "account_number": d.account_number,
        "policyholder_name": d.policyholder_name,
        "policy_number": d.policy_number,
        "claim_number": d.claim_number,
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
        "error_message": d.error_message,
        "email_error": d.email_error,
    }

@app.post("/document/{doc_id}/override")
def override_document(
    doc_id: int,
    override: dict = Body(...),
    db: Session = Depends(get_db),
):
    logger.info("=== OVERRIDE START doc_id=%s ===", doc_id)
    d = db.query(models.Document1).get(doc_id)
    if not d:
        logger.warning("Document %s not found for override", doc_id)
        raise HTTPException(status_code=404, detail="Document not found")

    orig = {
        "department": d.department,
        "category": d.category,
        "subcategory": d.subcategory,
        "summary": d.summary,
        "action_items": d.action_items,
    }
    classification_changed = False
    for field in orig:
        if override.get(field) is not None and override[field] != getattr(d, field):
            setattr(d, field, override[field])
            classification_changed = True
            logger.info(
                "Overriding %s: %r -> %r",
                field, orig[field], override[field]
            )

    if not classification_changed:
        logger.info("No fields changed—no commit")
        return {
            **orig,
            "id": d.id,
            "status": d.status,
            "destination_bucket": d.destination_bucket,
            "destination_key": d.destination_key,
        }

    d.status = "Processed with Override"
    try:
        db.commit()
        db.refresh(d)
    except Exception as e:
        db.rollback()
        logger.exception("Override commit failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Override commit error: {e}")

    logger.info("Running synchronous reroute for doc_id=%s", doc_id)
    success, error_msg, new_bucket, new_key = process_document_destination(
        d, db, s3_client, AWS_S3_BUCKET
    )
    d.destination_bucket = new_bucket
    d.destination_key = new_key
    d.error_message = error_msg
    d.status = (
        "Processed with Override"
        if success
        else ("No Destination" if error_msg and error_msg.startswith("No matching") else "Failed")
    )
    try:
        db.commit()
        db.refresh(d)
        logger.info("Inline reroute completed: bucket=%s key=%s", new_bucket, new_key)
    except Exception as e:
        db.rollback()
        logger.exception("Reroute commit failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Reroute commit error: {e}")

    logger.info("=== OVERRIDE END doc_id=%s ===", doc_id)
    return {
        "id": d.id,
        "account_number": d.account_number,
        "policyholder_name": d.policyholder_name,
        "policy_number": d.policy_number,
        "claim_number": d.claim_number,
        "department": d.department,
        "category": d.category,
        "subcategory": d.subcategory,
        "summary": d.summary,
        "action_items": d.action_items,
        "status": d.status,
        "destination_bucket": d.destination_bucket,
        "destination_key": d.destination_key,
        "error_message": d.error_message,
        "email_error": d.email_error,
    }

@app.delete("/document/{doc_id}", status_code=204)
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    d = db.query(models.Document1).filter(models.Document1.id == doc_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(d)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.exception("Delete failed: %s", e)
        raise HTTPException(status_code=500, detail="Delete failed")

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
app.include_router(account_policy_router)
app.include_router(accounts_v1_router)                  
app.include_router(policies_v1_router)                  
app.include_router(claims_v1_router)  
app.include_router(webhook_router)                  
