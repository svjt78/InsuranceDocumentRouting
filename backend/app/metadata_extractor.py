# backend/app/metadata_extractor.py

import json
import logging
import openai

from .config import OPENAI_API_KEY

# Configure OpenAI API key
openai.api_key = OPENAI_API_KEY

# Logger for metadata extraction
logger = logging.getLogger("metadata_extractor")


def extract_metadata(subject: str, body: str, attachment_text: str) -> dict:
    """
    Extracts insurance metadata fields from email subject, body, and attachment text.
    Returns a dict with keys: account_number, policyholder_name, policy_number, claim_number.
    If any field is missing, returns "XXXX" as the default value.
    """
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
        # Call the LLM for metadata extraction
        resp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=256,
        )
        content = resp.choices[0].message.content.strip()
        data = json.loads(content)

        return {
            "account_number": data.get("account_number") or "XXXX",
            "policyholder_name": data.get("policyholder_name") or "XXXX",
            "policy_number": data.get("policy_number") or "XXXX",
            "claim_number": data.get("claim_number") or "XXXX",
        }

    except Exception as e:
        logger.exception("LLM metadata extraction failed: %s", e)
        # On failure, return default placeholders
        return {
            "account_number": "XXXX",
            "policyholder_name": "XXXX",
            "policy_number": "XXXX",
            "claim_number": "XXXX",
        }
