import os
import json
import logging
import threading

import boto3
import cv2
import numpy as np
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
from sqlalchemy.exc import SQLAlchemyError

from .config import AWS_S3_BUCKET, AWS_REGION, TESSERACT_CMD
from .database import SessionLocal
from .destination_service import process_document_destination
from .llm_classifier import classify_document
from .pii_masker import mask_pii
from .rabbitmq import get_rabbitmq_connection
from .notifications import notify_document  # our notifications module
from .models import Document1

# ─────────────────────────────────── Configure Tesseract ────────────────────────────────────
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

# ─────────────────────────────────── AWS S3 client ──────────────────────────────────────────
s3_client = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

# The bucket where input documents are stored
SOURCE_BUCKET = AWS_S3_BUCKET

logger = logging.getLogger("ocr_worker")
logger.setLevel(logging.INFO)


def fetch_s3_bytes(key: str) -> bytes:
    try:
        resp = s3_client.get_object(Bucket=SOURCE_BUCKET, Key=key)
        data = resp["Body"].read()
        logger.debug(f"Fetched {len(data)} bytes for key: {key}")
        return data
    except Exception as e:
        logger.exception(f"Failed to fetch S3 object: {e}")
        return b""


def ocr_from_image_bytes(image_bytes: bytes) -> str:
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        logger.error("cv2.imdecode failed")
        return ""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    pil_img = Image.fromarray(thresh)
    try:
        return pytesseract.image_to_string(pil_img)
    except Exception as e:
        logger.exception(f"Tesseract error: {e}")
        return ""


def ocr_from_pdf_bytes(pdf_bytes: bytes) -> str:
    try:
        pages = convert_from_bytes(pdf_bytes)
        if not pages:
            return ""
        return pytesseract.image_to_string(pages[0])
    except Exception as e:
        logger.exception(f"PDF conversion error: {e}")
        return ""


def perform_ocr(s3_key: str) -> str:
    logger.info(f"▶ Fetching and OCR’ing: {s3_key}")
    data = fetch_s3_bytes(s3_key)
    if not data:
        return ""
    ext = os.path.splitext(s3_key)[1].lower()
    if ext == ".pdf":
        return ocr_from_pdf_bytes(data)
    return ocr_from_image_bytes(data)


def sanitize_classification(raw: dict) -> dict:
    """
    Normalize LLM output: force strings and JSON‐serialize action_items.
    """
    department  = str(raw.get("department", "") or "")
    category    = str(raw.get("category", "") or "")
    subcategory = str(raw.get("subcategory", "") or "")
    summary     = str(raw.get("summary", "") or "")

    ai_raw = raw.get("action_items", "")
    if isinstance(ai_raw, list):
        action_items = json.dumps(ai_raw)
    else:
        action_items = str(ai_raw or "")

    return {
        "department":   department,
        "category":     category,
        "subcategory":  subcategory,
        "summary":      summary,
        "action_items": action_items,
    }


def process_document(ch, method, properties, body):
    logger.info(f"▶ Received message: {body}")
    db = SessionLocal()
    try:
        msg = json.loads(body)
        doc_id = msg.get("doc_id")
        s3_key = msg.get("s3_key")
        logger.info(f"🔍 Processing doc_id={doc_id}, s3_key={s3_key}")

        # 1) OCR
        extracted_text = perform_ocr(s3_key)

        # 2) Classification
        raw_cls = classify_document(extracted_text)
        cls = sanitize_classification(raw_cls)
        logger.info(f"🤖 Classification: {cls}")

        if cls["summary"]:
            cls["summary"] = mask_pii(cls["summary"])
            logger.debug("🔒 PII masked in summary")

        # 3) Fetch & update Document1 record
        document = db.get(Document1, doc_id)
        if not document:
            logger.warning(f"Document not found: {doc_id}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        document.extracted_text  = extracted_text
        document.department      = cls["department"]
        document.category        = cls["category"]
        document.subcategory     = cls["subcategory"]
        document.summary         = cls["summary"]
        document.action_items    = cls["action_items"]

        # 4) Routing / copy
        logger.info("📦 Running destination service")
        success, error_msg, dest_bucket, dest_key = process_document_destination(
            document, db, s3_client, SOURCE_BUCKET
        )
        if success:
            document.destination_bucket = dest_bucket
            document.destination_key   = dest_key
            document.status            = "Processed"
            document.error_message     = None
            logger.info(f"✅ Copied to {dest_bucket}/{dest_key}")
        else:
            document.status = (
                "No Destination"
                if error_msg.startswith("No matching")
                else "Failed"
            )
            document.error_message = error_msg
            logger.warning(f"⚠ Destination failed: {error_msg}")

        db.commit()
        logger.info(f"✔ DocID={doc_id} status={document.status}")

        # 5) Acknowledge RabbitMQ
        ch.basic_ack(delivery_tag=method.delivery_tag)

        # 6) Fire off notification in background
        try:
            threading.Thread(
                target=notify_document,
                args=(doc_id, False),  # overridden=False
                daemon=True
            ).start()
        except Exception as e:
            logger.exception(f"Failed to spawn notification thread: {e}")

    except SQLAlchemyError as db_err:
        logger.exception(f"🛑 DB Error: {db_err}")
        db.rollback()
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    except Exception as e:
        logger.exception(f"🛑 Unexpected error: {e}")
        db.rollback()
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    finally:
        db.close()


def start_ocr_worker():
    conn = get_rabbitmq_connection()
    ch   = conn.channel()
    queue_name = "document_queue"

    ch.queue_declare(queue=queue_name, durable=True)
    ch.basic_qos(prefetch_count=1)
    ch.basic_consume(
        queue=queue_name,
        on_message_callback=process_document
    )

    logger.info("🚀 OCR Worker started, waiting for messages…")
    ch.start_consuming()


if __name__ == "__main__":
    start_ocr_worker()
