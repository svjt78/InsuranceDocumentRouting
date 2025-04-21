# backend/app/ocr_worker.py

import os
import json
import logging

import boto3
import cv2
import numpy as np
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
from sqlalchemy.exc import SQLAlchemyError

from .config import MINIO_ENDPOINT, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, TESSERACT_CMD
from .database import SessionLocal
from .destination_service import process_document_destination
from .llm_classifier import classify_document
from .pii_masker import mask_pii
from .rabbitmq import get_rabbitmq_connection

# Configure Tesseract
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

# S3 client
s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)

SOURCE_BUCKET = os.getenv("MINIO_BUCKET", "documents")

logger = logging.getLogger("ocr_worker")
logger.setLevel(logging.INFO)

def fetch_s3_bytes(key: str) -> bytes:
    try:
        response = s3_client.get_object(Bucket=SOURCE_BUCKET, Key=key)
        data = response["Body"].read()
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
    return ocr_from_pdf_bytes(data) if ext == ".pdf" else ocr_from_image_bytes(data)

import json

def sanitize_classification(raw: dict) -> dict:
    """
    Normalize the LLM output:

    • Always return strings for the text‑fields.
    • Serialize action_items to a JSON array (["item1", "item2", …]) when the
      classifier gives a list, so the frontend can safely `JSON.parse()` it.
    """
    # Department / category / etc. — force to string, fallback to ""
    department  = str(raw.get("department", "")  or "")
    category    = str(raw.get("category", "")    or "")
    subcategory = str(raw.get("subcategory", "") or "")
    summary     = str(raw.get("summary", "")     or "")

    # Action items — handle list vs. string vs. missing
    ai_raw = raw.get("action_items", "")
    if isinstance(ai_raw, list):
        action_items = json.dumps(ai_raw)           # valid JSON array
    else:
        action_items = str(ai_raw or "")

    return {
        "department":  department,
        "category":    category,
        "subcategory": subcategory,
        "summary":     summary,
        "action_items": action_items,
    }


def process_document(ch, method, properties, body):
    logger.info(f"▶ Received: {body}")
    db = SessionLocal()
    try:
        message = json.loads(body)
        doc_id = message.get("doc_id")
        s3_key = message.get("s3_key")
        logger.info(f"🔍 Processing doc_id={doc_id}, s3_key={s3_key}")

        extracted_text = perform_ocr(s3_key)
        raw_result = classify_document(extracted_text)
        classification = sanitize_classification(raw_result)
        logger.info(f"🤖 Classification: {classification}")

        if classification["summary"]:
            classification["summary"] = mask_pii(classification["summary"])
            logger.debug("🔒 PII masked")

        from .models import Document
        document = db.query(Document).get(doc_id)
        if not document:
            logger.warning(f"Document not found: {doc_id}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        # Update document fields
        document.extracted_text = extracted_text
        document.department = classification["department"]
        document.category = classification["category"]
        document.subcategory = classification["subcategory"]
        document.summary = classification["summary"]
        document.action_items = classification["action_items"]

        logger.info("📦 Running destination service")
        success, error_msg, dest_bucket, dest_key = process_document_destination(
            document, db, s3_client, SOURCE_BUCKET
        )

        if success:
            document.destination_bucket = dest_bucket
            document.destination_key = dest_key
            document.status = "Processed"
            document.error_message = None
            logger.info(f"✅ Document copied to {dest_bucket}/{dest_key}")
        else:
            document.status = "No Destination" if error_msg.startswith("No matching") else "Failed"
            document.error_message = error_msg
            logger.warning(f"⚠ Destination failed: {error_msg}")

        db.commit()
        logger.info(f"✔ DocID={doc_id} status={document.status}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

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
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    queue_name = "document_queue"
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=process_document)
    logger.info("🚀 OCR Worker started and listening...")
    channel.start_consuming()

if __name__ == "__main__":
    start_ocr_worker()
