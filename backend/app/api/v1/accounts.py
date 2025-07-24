# backend/app/api/v1/accounts.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...service.hierarchy import fetch_docs_by_account, build_account_hierarchy
from ...model_schemas.api_v1 import AccountResponse
from ...models import Document1
from app.database import SessionLocal

router = APIRouter(prefix="/api/v1/accounts", tags=["accounts"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get(
    "/{identifier}",
    response_model=AccountResponse,
    response_model_exclude_none=True
)
def get_account(identifier: str, db: Session = Depends(get_db)):
    """
    Retrieve account hierarchy by account number or policyholder name.
    """
    # Try account number lookup
    docs = fetch_docs_by_account(db, identifier)

    # Fallback to policyholder name lookup if no docs found
    if not docs:
        docs = (
            db
            .query(Document1)
            .filter(Document1.policyholder_name == identifier)
            .all()
        )

    if not docs:
        raise HTTPException(status_code=404, detail="Account or policyholder not found")

    return build_account_hierarchy(docs)
