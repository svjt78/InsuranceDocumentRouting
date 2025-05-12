# config.py
import os
from dotenv import load_dotenv
from pathlib import Path

# Load the .env file from parent directory (backend/.env)
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")
RABBITMQ_URL = os.getenv("RABBITMQ_URL")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_BUCKET = os.getenv("MINIO_BUCKET")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TESSERACT_CMD = os.getenv("TESSERACT_CMD")

# Email (Resend) settings
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", "no-reply@yourdomain.com")

# Presigned URL TTL (in seconds)
PRESIGNED_URL_EXPIRES_IN = int(os.getenv("PRESIGNED_URL_EXPIRES_IN", "3600"))
