import os
import logging
import re
from typing import Optional, Tuple
from botocore.exceptions import ClientError

from .config import AWS_REGION, AWS_S3_BUCKET
from .models import BucketMapping

logger = logging.getLogger(__name__)


def _sanitize_segment(name: str) -> str:
    """
    Convert an arbitrary name into a safe S3 segment:
      - lowercase
      - letters, numbers, hyphens only
      - no leading/trailing hyphens
      - 3–63 chars
      - spaces/underscores → hyphens
    """
    seg = (name or "").strip().lower()
    seg = re.sub(r"[_\s]+", "-", seg)
    seg = re.sub(r"[^a-z0-9-]", "", seg)
    seg = seg.strip('-')
    if len(seg) < 3:
        seg = seg.ljust(3, '0')
    if len(seg) > 63:
        seg = seg[:63]
    return seg


def process_document_destination(
    document,
    db,
    s3_client,
    source_bucket: str
) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
    """
    Copy the document into the root S3 bucket under the "output" prefix,
    using a hierarchical key based on account, policy, department, category,
    and subcategory (suffix) folders.

    Returns: (success, error_msg, destination_folder, destination_key)
    """
    try:
        # 1. Determine logical suffix from mapping or fallback to subcategory
        mapping = (
            db.query(BucketMapping)
              .filter_by(
                  department=document.department,
                  category=document.category,
                  subcategory=document.subcategory
              )
              .first()
        )
        if mapping and mapping.bucket_name:
            suffix = _sanitize_segment(mapping.bucket_name)
        else:
            suffix = _sanitize_segment(document.subcategory or "")
            # persist suffix-only mapping
            if not mapping:
                mapping = BucketMapping(
                    department=document.department,
                    category=document.category,
                    subcategory=document.subcategory,
                    bucket_name=suffix
                )
                db.add(mapping)
            else:
                mapping.bucket_name = suffix
            db.commit()
            db.refresh(mapping)

        # Always use the root bucket
        dest_bucket = AWS_S3_BUCKET

        # 2. Build object key path inside 'output/'
        segments = []
        acct = getattr(document, 'account_number', None)
        segments.append(_sanitize_segment(f"Account-{acct}")) if acct and acct != "XXXX" else segments.append('unknown-account')
        pol = getattr(document, 'policy_number', None)
        segments.append(_sanitize_segment(f"Policy-{pol}")) if pol and pol != "XXXX" else segments.append('unknown-policy')
        if (document.department or '').lower() == 'claims':
            claim = getattr(document, 'claim_number', None)
            if claim and claim != "XXXX":
                segments.append(_sanitize_segment(f"Claim-{claim}"))
        segments.extend([
            _sanitize_segment(document.department or ''),
            _sanitize_segment(document.category or ''),
            suffix
        ])
        filename = os.path.basename(document.s3_key)
        # prefix with 'output'
        destination_key = f"output/{'/'.join(segments)}/{filename}"

        # 3. Copy object
        copy_source = {'Bucket': source_bucket, 'Key': document.s3_key}
        s3_client.copy_object(
            Bucket=dest_bucket,
            CopySource=copy_source,
            Key=destination_key
        )
        logger.info(
            "Copied doc %s from %s/%s to %s/%s",
            document.id, source_bucket, document.s3_key,
            dest_bucket, destination_key
        )

        # Return the suffix (final folder) for UI, and the full key
        return True, None, suffix, destination_key

    except ClientError as ce:
        err = f"S3 error: {ce.response.get('Error', {}).get('Message', str(ce))}"
        logger.exception(err)
        return False, err, None, None
    except Exception as e:
        err = f"Unexpected error: {e}"
        logger.exception(err)
        return False, err, None, None
