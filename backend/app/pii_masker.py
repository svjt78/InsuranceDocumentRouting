# backend/app/pii_masker.py

import re
import logging

logger = logging.getLogger("pii_masker")

def mask_pii(text) -> str:
    """Mask PII patterns like SSNs in a text string."""
    if not isinstance(text, str):
        logger.warning("PII masking skipped: expected string but got %s", type(text))
        return ""

    # Example: Mask SSNs in format 123-45-6789
    ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
    masked_text = re.sub(ssn_pattern, '***-**-****', text)
    return masked_text
