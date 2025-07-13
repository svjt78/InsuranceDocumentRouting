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
    Recognizes these synonyms for account_number and policyholder_name:
      - account_number: Account, Acct, Account Number, Acct No, Account#, Acct#, Group Number, Group No, Group#
      - policyholder_name: Policyholder, Policy Holder, Policyholder Name, Group Name

    Returns a dict with keys: account_number, policyholder_name, policy_number, claim_number.
    If any field is missing, returns "XXXX" as the default value.
    """
    # Build prompt ensuring pure JSON response and escaping braces
    prompt = f"""
You are an assistant that extracts insurance metadata from text.  
You must respond with exactly one JSON object and nothing else, using these keys: \"account_number\", \"policyholder_name\", \"policy_number\", \"claim_number\".  
Use \"XXXX\" if a field is missing or empty.  
Examples of labels:  
- account_number may be labeled as Account, Acct, Account Number, Acct No, Account#, Acct#, Group Number, Group No, or Group#.  
- policyholder_name may be labeled as Policyholder, Policy Holder, Policyholder Name, or Group Name.  

Example response format:  
{{  
  "account_number": "12345",  
  "policyholder_name": "Acme Corp",  
  "policy_number": "54321",  
  "claim_number": "67890"  
}}  

Now extract from the following inputs:  
Subject: {subject}  
Body: {body}  
Attachment text: {attachment_text}  
"""
    try:
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
        logger.exception("Metadata extraction failed or invalid JSON: %s", e)
        return {
            "account_number": "XXXX",
            "policyholder_name": "XXXX",
            "policy_number": "XXXX",
            "claim_number": "XXXX",
        }
