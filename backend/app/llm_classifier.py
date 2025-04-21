# backend/app/llm_classifier.py  (replace file)

import openai, json, logging, time
from sqlalchemy.orm import Session
from .database import SessionLocal
from . import models
from .config import OPENAI_API_KEY

logger = logging.getLogger("llm_classifier")
openai.api_key = OPENAI_API_KEY

_CACHE_TTL = 600          # 10 minutes
_last_refresh = 0.0
_hierarchy_prompt = ""     # cached string

def _refresh_hierarchy_cache():
    global _last_refresh, _hierarchy_prompt
    if time.time() - _last_refresh < _CACHE_TTL:
        return
    db: Session = SessionLocal()
    try:
        rows = db.query(models.DocHierarchy).all()
        triples = sorted({(r.department, r.category, r.subcategory) for r in rows})
        lines = [
            f"- Department: {dep} | Category: {cat} | Sub‑category: {sub}"
            for dep, cat, sub in triples
        ]
        _hierarchy_prompt = "\n".join(lines)
        _last_refresh = time.time()
        logger.info("Hierarchy cache refreshed with %d triples", len(triples))
    finally:
        db.close()

def classify_document(extracted_text: str) -> dict:
    _refresh_hierarchy_cache()
    prompt = f"""
You are an insurance‑document classifier.  ONLY use a combination present below.
Hierarchy (do NOT invent new names):
{_hierarchy_prompt}

Classify the document and return valid JSON:
{{
 "department": "...",
 "category": "...",
 "subcategory": "...",
 "summary": "single paragraph; clauses separated by semicolons.",
 "action_items": ["First item", "Second item", …]   # numbered later in UI
}}

Document Text:
\"\"\"{extracted_text}\"\"\"
"""
    try:
        resp = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "Return ONLY the JSON object. No markdown."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
        )
        raw = resp.choices[0].message.content
        logger.debug("LLM raw: %s", raw)
        return json.loads(raw)
    except Exception as e:
        logger.exception("LLM failure: %s", e)
        return {}
