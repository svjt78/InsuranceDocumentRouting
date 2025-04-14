import cv2
import pytesseract
import numpy as np
from PIL import Image
import boto3
import json
from .config import MINIO_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, TESSERACT_CMD
from .rabbitmq import get_rabbitmq_connection
from .llm_classifier import classify_document
from .pii_masker import mask_pii

# Configure Tesseract command path
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

# Initialize minIO S3 client using boto3
s3_client = boto3.client(
    's3',
    endpoint_url=MINIO_URL,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY
)
BUCKET = 'documents'

def preprocess_image(image_data: bytes) -> Image.Image:
    # Convert bytes to a NumPy array
    nparr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    # Additional preprocessing (deskew, denoise) can be added here
    return Image.fromarray(thresh)

def perform_ocr(s3_key: str) -> str:
    response = s3_client.get_object(Bucket=BUCKET, Key=s3_key)
    data = response['Body'].read()
    processed_image = preprocess_image(data)
    text = pytesseract.image_to_string(processed_image)
    return text

def process_document(ch, method, properties, body):
    try:
        message = json.loads(body)
        s3_key = message.get('s3_key')
        doc_id = message.get('doc_id')

        # Run OCR on the document
        extracted_text = perform_ocr(s3_key)
        
        # Call LLM classifier to get classification and summarization
        classification = classify_document(extracted_text)
        
        # Mask sensitive info in summary
        if classification.get('summary'):
            classification['summary'] = mask_pii(classification['summary'])
        
        # Here, update the Document record in the DB (code omitted for brevity)
        print(f"DocID {doc_id} classified as: {classification}")
        
        # Acknowledge processed message
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"OCR worker error: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def start_ocr_worker():
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    queue_name = 'document_queue'
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=process_document)
    print("OCR Worker started and waiting for messages...")
    channel.start_consuming()

if __name__ == "__main__":
    start_ocr_worker()
