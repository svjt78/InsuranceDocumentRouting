# backend/app/destination_service.py

import logging
from botocore.exceptions import ClientError
from . import models

logger = logging.getLogger(__name__)

def process_document_destination(document, db, s3_client, source_bucket):
    """
    Look up the destination bucket for a document and copy the file from the source bucket.

    Parameters:
        document: The Document model instance.
        db: SQLAlchemy DB session.
        s3_client: boto3 S3 client.
        source_bucket: The source bucket name (e.g. "documents").

    Returns:
        A tuple (success, error_message, destination_bucket, destination_key).
        - success: True if destination lookup and file copy succeed.
        - error_message: Contains an error detail if processing fails.
        - destination_bucket: Name of the destination bucket.
        - destination_key: The key for the copied file in the destination bucket.
    """
    try:
        # Retrieve the bucket mapping that matches the document's classification.
        mapping = db.query(models.BucketMapping).filter_by(
            department=document.department,
            category=document.category,
            subcategory=document.subcategory
        ).first()

        if not mapping:
            error = "No matching destination mapping found."
            return (False, error, None, None)

        destination_bucket = mapping.bucket_name

        # Ensure the destination bucket is different from the source bucket.
        if destination_bucket == source_bucket:
            error = "Destination bucket cannot be the source bucket."
            return (False, error, None, None)

        # Check if the destination bucket exists; if not, create it.
        try:
            s3_client.head_bucket(Bucket=destination_bucket)
        except ClientError as e:
            error_code = e.response["Error"].get("Code", "")
            if error_code in ("404", "NoSuchBucket", "AccessDenied"):
                s3_client.create_bucket(Bucket=destination_bucket)
                logger.info("Created destination bucket: %s", destination_bucket)
            else:
                logger.exception("Error checking destination bucket: %s", e)
                return (False, f"Error checking destination bucket: {e}", None, None)

        # Determine the destination file key; for simplicity, reuse the same key.
        destination_key = document.s3_key

        # Copy the file from the source bucket to the destination bucket.
        copy_source = {'Bucket': source_bucket, 'Key': document.s3_key}
        try:
            s3_client.copy_object(
                CopySource=copy_source,
                Bucket=destination_bucket,
                Key=destination_key
            )
            logger.info("Copied document %s to destination bucket %s", document.id, destination_bucket)
            return (True, None, destination_bucket, destination_key)
        except ClientError as e:
            logger.exception("File copy failed: %s", e)
            return (False, f"File copy failed: {e}", None, None)

    except Exception as e:
        logger.exception("Unexpected error during destination processing: %s", e)
        return (False, f"Unexpected error: {e}", None, None)
