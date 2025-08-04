# backend/app/api/v1/email_webhook.py

from fastapi import APIRouter, HTTPException, Body, BackgroundTasks
from pydantic import BaseModel
import base64, uuid, logging

from app.database import SessionLocal
from app.models import Document1, MessageOutbox
from app.config import AWS_S3_BUCKET, S3_INPUT_PREFIX
from app.s3_client import s3_client
from app.metadata_extractor import extract_metadata
from app.ocr_worker import perform_ocr
from app.ws_manager import manager

router = APIRouter(prefix="/api/v1/ingest", tags=["ingest"])

class AttachmentIn(BaseModel):
    filename: str
    content_base64: str

class EmailWebhook(BaseModel):
    subject: str
    body: str
    attachments: list[AttachmentIn]

def process_webhook_email(subject: str, body: str, attachments: list[AttachmentIn]) -> list[int]:
    logger = logging.getLogger("email_webhook")
    created_ids = []

    for att in attachments:
        try:
            raw = base64.b64decode(att.content_base64)
        except Exception as e:
            logger.error("Invalid base64 for %s: %s", att.filename, e)
            # continue to next attachment
            continue

        # S3 upload
        key_name = f"{uuid.uuid4().hex}_{att.filename}"
        s3_key = f"{S3_INPUT_PREFIX.rstrip('/')}/{key_name}"
        try:
            s3_client.put_object(Bucket=AWS_S3_BUCKET, Key=s3_key, Body=raw)
        except Exception:
            logger.exception("S3 upload failed for %s", att.filename)
            continue

        # OCR
        try:
            ocr_text = perform_ocr(s3_key)
        except Exception as e:
            logger.warning("OCR failed for %s: %s", att.filename, e)
            ocr_text = ""

        # Metadata
        try:
            meta = extract_metadata(subject, body, ocr_text)
        except Exception:
            meta = {
                "account_number": "XXXX",
                "policyholder_name": "XXXX",
                "policy_number": "XXXX",
                "claim_number": "XXXX"
            }

        # Insert Document1
        db = SessionLocal()
        try:
            doc = Document1(
                filename=att.filename,
                s3_key=s3_key,
                extracted_text=ocr_text,
                status="Pending",
                **meta
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)
            created_ids.append(doc.id)
        except Exception:
            db.rollback()
            logger.exception("DB insert failed for %s", att.filename)
        finally:
            db.close()

        # Enqueue outbox
        db2 = SessionLocal()
        try:
            out = MessageOutbox(
                exchange="",
                routing_key="document_queue",
                payload={"document_id": doc.id, "s3_key": s3_key}
            )
            db2.add(out)
            db2.commit()
        except Exception:
            db2.rollback()
            logger.exception("Outbox enqueue failed for doc %s", doc.id)
        finally:
            db2.close()

    return created_ids

@router.post("/email-webhook")
async def ingest_via_webhook(
    payload: EmailWebhook,
    background_tasks: BackgroundTasks
):
    doc_ids = process_webhook_email(payload.subject, payload.body, payload.attachments)
    for did in doc_ids:
        background_tasks.add_task(
            manager.broadcast,
            {"type": "new_document", "document_id": did}
        )
    return {"ingested_count": len(doc_ids), "document_ids": doc_ids}
