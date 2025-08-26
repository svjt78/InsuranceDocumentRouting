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
    Uses priority-based extraction: Attachment document text > Email body > Email subject.
    
    Recognizes these synonyms for account_number and policyholder_name:
      - account_number: Account, Acct, Account Number, Acct No, Account#, Acct#, Group Number, Group No, Group#
      - policyholder_name: Policyholder, Policy Holder, Policyholder Name, Group Name

    Returns a dict with keys: account_number, policyholder_name, policy_number, claim_number.
    If any field is missing, returns "XXXX" as the default value.
    """
    # Build prompt with explicit priority instructions
    prompt = f"""
You are an assistant that extracts insurance metadata from text sources with STRICT PRIORITY RULES.

CRITICAL PRIORITY ORDER (MUST BE FOLLOWED):
1. HIGHEST PRIORITY: Attachment document text
2. MEDIUM PRIORITY: Email body  
3. LOWEST PRIORITY: Email subject

EXTRACTION RULES:
- ALWAYS prioritize information from attachment document text over email body or subject
- ONLY use email body information if the field is NOT found in attachment document text
- ONLY use email subject information if the field is NOT found in BOTH attachment document text AND email body
- If the same field appears in multiple sources, ALWAYS choose the value from the highest priority source
- You must respond with exactly one JSON object and nothing else

FIELD MAPPINGS:
- account_number may be labeled as: Account, Acct, Account Number, Acct No, Account#, Acct#, Group Number, Group No, Group#
- policyholder_name may be labeled as: Policyholder, Policy Holder, Policyholder Name, Group Name
- claim_number may be labeled as: Claim number, Claim, CLM, CLM#
- policy_number may be labeled as: Policy Number, Policy No, Policy#

RESPONSE FORMAT (use "XXXX" if field is missing from ALL sources):
{{
  "account_number": "value_from_highest_priority_source",
  "policyholder_name": "value_from_highest_priority_source", 
  "policy_number": "value_from_highest_priority_source",
  "claim_number": "value_from_highest_priority_source"
}}

TEXT SOURCES (in priority order):

1. ATTACHMENT DOCUMENT TEXT (HIGHEST PRIORITY):
{attachment_text if attachment_text.strip() else "No attachment text provided"}

2. EMAIL BODY (MEDIUM PRIORITY):
{body if body.strip() else "No email body provided"}

3. EMAIL SUBJECT (LOWEST PRIORITY):
{subject if subject.strip() else "No email subject provided"}

REMEMBER: Use attachment document text values first, fall back to email body only if not found in attachment, and use email subject only as last resort. Extract metadata following the priority rules above.
"""

    try:
        resp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=256,
        )
        content = resp.choices[0].message.content.strip()
        
        # Log the extraction decision for debugging
        logger.debug("LLM response for priority-based extraction: %s", content)
        
        data = json.loads(content)
        
        # Ensure we have valid values and log the source priority used
        result = {
            "account_number": data.get("account_number") or "XXXX",
            "policyholder_name": data.get("policyholder_name") or "XXXX", 
            "policy_number": data.get("policy_number") or "XXXX",
            "claim_number": data.get("claim_number") or "XXXX",
        }
        
        # Log which sources were available for debugging
        sources_available = []
        if attachment_text and attachment_text.strip():
            sources_available.append("attachment")
        if body and body.strip():
            sources_available.append("body")  
        if subject and subject.strip():
            sources_available.append("subject")
        
        logger.info("Priority-based extraction completed. Sources available: %s, Results: %s", 
                   sources_available, result)
        
        return result
        
    except json.JSONDecodeError as e:
        logger.exception("JSON decode error in priority-based extraction: %s", e)
        return {
            "account_number": "XXXX",
            "policyholder_name": "XXXX",
            "policy_number": "XXXX", 
            "claim_number": "XXXX",
        }
    except Exception as e:
        logger.exception("Priority-based metadata extraction failed: %s", e)
        return {
            "account_number": "XXXX",
            "policyholder_name": "XXXX",
            "policy_number": "XXXX",
            "claim_number": "XXXX",
        }