# backend/app/api/v1/claims.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...service.hierarchy import fetch_docs_by_claim, build_claim_hierarchy
from ...model_schemas.api_v1 import ClaimResponse
from app.database import SessionLocal

router = APIRouter(prefix="/api/v1/claims", tags=["claims"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get(
    "/{claim_number}",
    response_model=ClaimResponse,
    response_model_exclude_none=True
)
def get_claim(claim_number: str, db: Session = Depends(get_db)):
    """
    Retrieve claim hierarchy for a given claim number.
    """
    docs = fetch_docs_by_claim(db, claim_number)
    if not docs:
        raise HTTPException(status_code=404, detail="Claim not found")
    return build_claim_hierarchy(docs)
