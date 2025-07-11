# backend/app/email_worker.py

import os
import io
import time
import uuid
import json
import logging
import imaplib
import email
from email.header import decode_header

import boto3
import openai
import asyncio
from sqlalchemy.orm import Session

from .database import SessionLocal
from . import models
from .config import AWS_REGION, AWS_S3_BUCKET, S3_INPUT_PREFIX, OPENAI_API_KEY
from .ws_manager import manager  # ← import WebSocket manager for broadcasting

# ─────────────────────────────────── Configuration & Clients ─────────────────────────────────
logger = logging.getLogger("email_worker")
logging.basicConfig(level=logging.INFO)

# Gmail IMAP settings
IMAP_SERVER         = os.getenv("IMAP_SERVER", "imap.gmail.com")
IMAP_PORT           = int(os.getenv("IMAP_PORT", "993"))
GMAIL_EMAIL         = os.getenv("GMAIL_EMAIL")
GMAIL_APP_PASSWORD  = os.getenv("GMAIL_APP_PASSWORD")
EMAIL_POLL_INTERVAL = int(os.getenv("EMAIL_POLL_INTERVAL", "60"))  # seconds

# AWS S3 settings from config
# AWS_REGION, AWS_S3_BUCKET, S3_INPUT_PREFIX imported

# OpenAI settings
openai.api_key = OPENAI_API_KEY

# Validate required env
for var_name, var_value in (
    ("GMAIL_EMAIL", GMAIL_EMAIL),
    ("GMAIL_APP_PASSWORD", GMAIL_APP_PASSWORD),
    ("AWS_S3_BUCKET", AWS_S3_BUCKET),
    ("OPENAI_API_KEY", openai.api_key),
):
    if not var_value:
        logger.error("Missing required environment variable: %s", var_name)
        raise RuntimeError(f"Environment variable {var_name} is not set")

# Initialize clients
imap_client = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
s3_client   = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

# ─────────────────────────────────── Helper: extract metadata via LLM ─────────────────────────
def extract_metadata(subject: str, body: str, attachment_text: str) -> dict:
    prompt = f"""
You are an assistant that extracts insurance fields from email and document text. If a field is missing, return "XXXX".

Example:
Subject: "Policy Update"
Body: "Hello, Account: 12345; Policyholder: Jane Smith"
Attachment text: "Claim Number: 67890; Policy Number: 54321"
Output:
{{
  "account_number": "12345",
  "policyholder_name": "Jane Smith",
  "policy_number": "54321",
  "claim_number": "67890"
}}

Now process:
Email subject and body:
{subject}\n{body}

Attachment text:
{attachment_text}
"""
    try:
        resp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=256
        )
        content = resp.choices[0].message.content.strip()
        data = json.loads(content)
        return {
            "account_number":    data.get("account_number")    or "XXXX",
            "policyholder_name": data.get("policyholder_name") or "XXXX",
            "policy_number":     data.get("policy_number")     or "XXXX",
            "claim_number":      data.get("claim_number")      or "XXXX",
        }
    except Exception as e:
        logger.exception("LLM metadata extraction failed: %s", e)
        return {
            "account_number":    "XXXX",
            "policyholder_name": "XXXX",
            "policy_number":     "XXXX",
            "claim_number":      "XXXX",
        }

# ─────────────────────────────────── Process single email ─────────────────────────────────────
def process_message(msg: email.message.Message):
    # Decode subject
    subj, encoding = decode_header(msg.get("Subject"))[0]
    if isinstance(subj, bytes):
        subj = subj.decode(encoding or "utf-8", errors="ignore")
    # Extract plaintext body
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode(
                    part.get_content_charset() or "utf-8", errors="ignore"
                )
                break
    else:
        body = msg.get_payload(decode=True).decode(
            msg.get_content_charset() or "utf-8", errors="ignore"
        )

    # Find attachments
    attachments = [p for p in msg.walk() if p.get_content_disposition() == "attachment"]
    if not attachments:
        logger.info("Email has no attachments; skipping")
        return

    for part in attachments:
        raw_fname = part.get_filename()
        if not raw_fname:
            continue
        fname, enc = decode_header(raw_fname)[0]
        if isinstance(fname, bytes):
            fname = fname.decode(enc or "utf-8", errors="ignore")
        content = part.get_payload(decode=True)

        # Unique S3 key
        file_id = str(uuid.uuid4())
        key_name = f"{file_id}_{fname}"
        s3_key = f"{S3_INPUT_PREFIX}/{key_name}"

        # Upload to S3
        try:
            s3_client.put_object(Bucket=AWS_S3_BUCKET, Key=s3_key, Body=content)
            logger.info("Uploaded attachment to S3: %s", s3_key)
        except Exception as e:
            logger.exception("Failed to upload attachment to S3: %s", e)
            # Record failure in documents1
            db_fail: Session = SessionLocal()
            try:
                fail_doc = models.Document1(
                    filename=fname,
                    s3_key=s3_key,
                    extracted_text=None,
                    status="Failed",
                    error_message=str(e),
                    account_number="XXXX",
                    policyholder_name="XXXX",
                    policy_number="XXXX",
                    claim_number="XXXX"
                )
                db_fail.add(fail_doc)
                db_fail.commit()
            finally:
                db_fail.close()
            continue

        # OCR
        if fname.lower().endswith(".pdf"):
            text_data = ocr_from_pdf_bytes(content)
        else:
            text_data = ocr_from_image_bytes(content)

        # Extract metadata
        metadata = extract_metadata(subj, body, text_data)

        # Persist Document1
        db: Session = SessionLocal()
        try:
            doc = models.Document1(
                filename=fname,
                s3_key=s3_key,
                extracted_text=text_data,
                status="Pending",
                **metadata
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)
            logger.info("Created Document1 record id=%s", doc.id)

            # Broadcast new document event
            asyncio.create_task(
                manager.broadcast({"type": "new_document", "document_id": doc.id})
            )
        except Exception as e:
            db.rollback()
            logger.exception("DB insert failed: %s", e)
            # Record failed status
            try:
                db.add(models.Document1(
                    filename=fname,
                    s3_key=s3_key,
                    extracted_text=text_data,
                    status="Failed",
                    error_message=str(e),
                    **{k: metadata.get(k, "XXXX") for k in [
                        "account_number", "policyholder_name", "policy_number", "claim_number"
                    ]}
                ))
                db.commit()
            except Exception:
                db.rollback()
            finally:
                db.close()
            continue

        # Insert into outbox instead of direct publish
        db_out: Session = SessionLocal()
        try:
            out = models.MessageOutbox(
                exchange="",
                routing_key="document_queue",
                payload={"doc_id": doc.id, "s3_key": s3_key}
            )
            db_out.add(out)
            db_out.commit()
            logger.info("Enqueued message_outbox id=%s", out.id)
        except Exception as e:
            db_out.rollback()
            logger.exception("Failed to write to outbox: %s", e)
        finally:
            db_out.close()

# ─────────────────────────────────── Main polling loop ──────────────────────────────────────
def main():
    try:
        imap_client.login(GMAIL_EMAIL, GMAIL_APP_PASSWORD)
        logger.info("Logged in to IMAP server: %s", IMAP_SERVER)
    except Exception as e:
        logger.exception("IMAP login failed: %s", e)
        return

    while True:
        try:
            imap_client.select("INBOX")
            status, messages = imap_client.search(None, "UNSEEN")
            if status != "OK":
                logger.warning("IMAP search failed: %s", status)
                time.sleep(EMAIL_POLL_INTERVAL)
                continue

            for num in messages[0].split():
                try:
                    res, data = imap_client.fetch(num, "(RFC822)")
                    msg = email.message_from_bytes(data[0][1])
                    process_message(msg)
                    imap_client.store(num, '+FLAGS', '\\Seen')
                except Exception as e:
                    logger.exception("Error processing message %s: %s", num, e)

        except Exception as e:
            logger.exception("Email polling loop error: %s", e)

        time.sleep(EMAIL_POLL_INTERVAL)

if __name__ == "__main__":
    main()
