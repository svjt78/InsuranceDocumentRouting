import re

def mask_pii(text: str) -> str:
    # Mask SSNs in formats like 123-45-6789
    ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
    masked_text = re.sub(ssn_pattern, '***-**-****', text)
    return masked_text
