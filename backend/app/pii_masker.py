import re
import logging
from typing import Any, Union

logger = logging.getLogger("pii_masker")

# Precompiled PII patterns for efficient masking
en_patterns = {
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    # Extend with other patterns as needed, e.g., credit card, phone
}

def mask_pii(text: Union[str, Any]) -> str:
    """
    Mask PII patterns (e.g., SSNs) in the provided text. If input is not a string,
    returns an empty string and logs a warning.
    """
    if not isinstance(text, str):
        logger.warning("PII masking skipped: expected str but got %s", type(text))
        return ""

    masked_text = text
    # Mask Social Security Numbers
    masked_text = en_patterns["ssn"].sub("***-**-****", masked_text)

    # Add additional masking here if new patterns are configured
    return masked_text
