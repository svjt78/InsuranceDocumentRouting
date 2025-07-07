import json
import logging
import time

import openai
from .config import OPENAI_API_KEY
from .database import SessionLocal
from .models import DocHierarchy

logger = logging.getLogger("llm_classifier")
openai.api_key = OPENAI_API_KEY

# Cache settings
_CACHE_TTL = 600  # seconds
_last_refresh = 0.0
_hierarchy_prompt = ""

def _refresh_hierarchy_cache():
    """
    Refresh the in-memory hierarchy prompt from the DocHierarchy table every *_CACHE_TTL* seconds.
    """
    global _last_refresh, _hierarchy_prompt
    if time.time() - _last_refresh < _CACHE_TTL:
        return
    db = SessionLocal()
    try:
        rows = db.query(DocHierarchy).all()
        triples = sorted({(r.department, r.category, r.subcategory) for r in rows})
        lines = [f"- Department: {dep} | Category: {cat} | Sub-category: {sub}" for dep, cat, sub in triples]
        _hierarchy_prompt = "\n".join(lines)
        _last_refresh = time.time()
        logger.info("Hierarchy cache refreshed with %d triples", len(triples))
    finally:
        db.close()

def classify_document(extracted_text: str) -> dict:
    """
    Calls the LLM to classify a document according to the DocHierarchy and extracts a summary and action items.
    Returns a dict with keys: department, category, subcategory, summary, action_items.
    """
    _refresh_hierarchy_cache()
    prompt = f"""
You are an insurance-document classifier. ONLY use the exact department/category/sub-category combos below.

Hierarchy (do NOT invent new names):
{_hierarchy_prompt}

Return ONLY a JSON object with the following keys:
{{
  "department": "...",
  "category": "...",
  "subcategory": "...",
  "summary": "single paragraph; clauses separated by semicolons.",
  "action_items": ["First item", "Second item", …]
}}

Document Text:
{extracted_text}
"""
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Return ONLY the JSON object. No markdown."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
        )
        raw = response.choices[0].message.content.strip()
        logger.debug("LLM raw output: %s", raw)
        return json.loads(raw)
    except Exception as e:
        logger.exception("LLM classification failure: %s", e)
        return {}
