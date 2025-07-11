# backend/app/api/account_policy.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from pydantic import BaseModel

from ..database import SessionLocal
from ..models import Document1

router = APIRouter(prefix="/accounts", tags=["Accounts"])

# ─── Schemas ─────────────────────────────────────────────────────────────────────────────

class DocumentSchema(BaseModel):
    id: int
    filename: str
    s3_key: str
    department: Optional[str]

class ClaimSchema(BaseModel):
    claim_number: str
    documents: List[DocumentSchema]

class DepartmentSchema(BaseModel):
    department: str
    documents: Optional[List[DocumentSchema]] = None
    claims: Optional[List[ClaimSchema]] = None

class PolicySchema(BaseModel):
    policy_number: str
    departments: List[DepartmentSchema]

class AccountSchema(BaseModel):
    account_number: str
    policyholder_name: str
    policies: List[PolicySchema]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─── Endpoint ─────────────────────────────────────────────────────────────────────────────

@router.get("/", response_model=List[AccountSchema])
def list_accounts(db: Session = Depends(get_db)):
    # Fetch all documents
    docs = db.query(Document1).all()

    # Group into Account → Policy → Department → (Docs or Claims)
    grouping: Dict[str, Dict] = {}
    for d in docs:
        acct = grouping.setdefault(
            d.account_number,
            {
                "account_number": d.account_number,
                "policyholder_name": d.policyholder_name,
                "policies": {}
            }
        )
        pol = acct["policies"].setdefault(
            d.policy_number,
            {"policy_number": d.policy_number, "departments": {}}
        )

        dept_name = d.department or "Unknown"
        dept = pol["departments"].setdefault(
            dept_name,
            {"department": dept_name}
        )

        if dept_name == "Claims":
            cla_map = dept.setdefault("claims", {})
            cla = cla_map.setdefault(
                d.claim_number,
                {"claim_number": d.claim_number, "documents": []}
            )
            cla["documents"].append({
                "id": d.id,
                "filename": d.filename,
                "s3_key": d.s3_key,
                "department": d.department
            })
        else:
            docs_list = dept.setdefault("documents", [])
            docs_list.append({
                "id": d.id,
                "filename": d.filename,
                "s3_key": d.s3_key,
                "department": d.department
            })

    # Build Pydantic models for response
    result: List[AccountSchema] = []
    for acct_data in grouping.values():
        policies: List[PolicySchema] = []
        for pol_data in acct_data["policies"].values():
            departments: List[DepartmentSchema] = []
            for dept_data in pol_data["departments"].values():
                if dept_data["department"] == "Claims":
                    claims_list: List[ClaimSchema] = []
                    for cla_data in dept_data.get("claims", {}).values():
                        claims_list.append(ClaimSchema(**cla_data))
                    departments.append(
                        DepartmentSchema(department=dept_data["department"], claims=claims_list)
                    )
                else:
                    docs_list: List[DocumentSchema] = []
                    for doc_data in dept_data.get("documents", []):
                        docs_list.append(DocumentSchema(**doc_data))
                    departments.append(
                        DepartmentSchema(department=dept_data["department"], documents=docs_list)
                    )
            policies.append(
                PolicySchema(policy_number=pol_data["policy_number"], departments=departments)
            )
        result.append(
            AccountSchema(
                account_number=acct_data["account_number"],
                policyholder_name=acct_data["policyholder_name"],
                policies=policies
            )
        )

    return result
