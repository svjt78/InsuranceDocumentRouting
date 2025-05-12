# backend/app/notifications.py

import os
from typing import Optional
from sqlalchemy.orm import Session
from jinja2 import Environment, FileSystemLoader, select_autoescape

from .database import SessionLocal
from .models import EmailSetting, Document
from .resend_client import send_email

# Point Jinja2 at the real templates folder beside this module
BASE_DIR = os.path.dirname(__file__)
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

_env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(["html", "xml"]),
)

def _get_recipients(department: str, db: Session) -> list[str]:
    setting = (
        db.query(EmailSetting)
           .filter(EmailSetting.department == department)
           .first()
    )
    if not setting or not setting.email_addresses:
        return []
    return [e.strip() for e in setting.email_addresses.split(",")]

def _render_body(template_name: str, context: dict) -> str:
    tpl = _env.get_template(template_name)
    return tpl.render(**context)

def notify_document(
    doc_id: int,
    overridden: bool = False
) -> None:
    """
    Fetch document by ID, build email, send via Resend.
    On error, write the exception into document.email_error.
    """
    db = SessionLocal()
    try:
        doc = db.query(Document).get(doc_id)
        if not doc:
            return

        recipients = _get_recipients(doc.department, db)
        if not recipients:
            return  # nothing to do

        # Choose subject
        prefix = "Overridden: " if overridden else ""
        subject = f"{prefix}{doc.filename}"

        # Build context for template
        context = {
            "filename": doc.filename,
            "status": doc.status,
            "department": doc.department,
            "category": doc.category,
            "subcategory": doc.subcategory,
            "created_at": doc.created_at,
            "updated_at": doc.updated_at,
            "extracted_text": doc.extracted_text,
            "summary": doc.summary,
            "action_items": (
                doc.action_items
                if isinstance(doc.action_items, list)
                else (doc.action_items or "").split(";")
            ),
            "link": f"{doc.destination_bucket or os.getenv('MINIO_BUCKET')}/{doc.destination_key or doc.s3_key}"
        }

        # Render HTML body
        html_body = _render_body("email_notification.html", context)

        # Send via Resend
        send_email(recipients, subject, html_body)

        # Clear any previous error
        doc.email_error = None
        db.commit()

    except Exception as e:
        # Record the error on the document for visibility/retry
        db.rollback()
        if 'doc' in locals():
            doc.email_error = str(e)
            db.add(doc)
            db.commit()
    finally:
        db.close()
