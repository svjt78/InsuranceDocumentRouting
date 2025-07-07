# backend/app/config.py

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from backend/.env
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Database & messaging
DATABASE_URL   = os.getenv("DATABASE_URL")
RABBITMQ_URL   = os.getenv("RABBITMQ_URL")

# Outbox publisher settings
# Interval (in seconds) at which the outbox_publisher polls for unsent messages
OUTBOX_POLL_INTERVAL = int(os.getenv("OUTBOX_POLL_INTERVAL", "5"))

# AWS S3 configuration (replacing MinIO)
AWS_ACCESS_KEY_ID     = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION            = os.getenv("AWS_REGION", "us-east-1")
AWS_S3_BUCKET         = os.getenv("AWS_S3_BUCKET")

# S3 prefixes for input (uploads & email attachments) and output (processed)
S3_INPUT_PREFIX  = os.getenv("S3_INPUT_PREFIX", "input/documents")
S3_OUTPUT_PREFIX = os.getenv("S3_OUTPUT_PREFIX", "output")

# OpenAI & OCR
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TESSERACT_CMD  = os.getenv("TESSERACT_CMD")

# Email (Resend) settings
RESEND_API_KEY    = os.getenv("RESEND_API_KEY")
RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", "no-reply@yourdomain.com")

# Presigned URL TTL (in seconds; used for private S3 object access)
PRESIGNED_URL_EXPIRES_IN = int(os.getenv("PRESIGNED_URL_EXPIRES_IN", "3600"))
