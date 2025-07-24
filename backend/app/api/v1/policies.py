# backend/app/api/v1/policies.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...service.hierarchy import fetch_docs_by_policy, build_policy_hierarchy
from ...model_schemas.api_v1 import PolicyResponse
from app.database import SessionLocal

router = APIRouter(prefix="/api/v1/policies", tags=["policies"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get(
    "/{policy_number}",
    response_model=PolicyResponse,
    response_model_exclude_none=True
)
def get_policy(policy_number: str, db: Session = Depends(get_db)):
    """
    Retrieve policy hierarchy for a given policy number.
    """
    docs = fetch_docs_by_policy(db, policy_number)
    if not docs:
        raise HTTPException(status_code=404, detail="Policy not found")
    return build_policy_hierarchy(docs)
