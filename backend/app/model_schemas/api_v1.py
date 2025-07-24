# backend/app/schemas/api_v1.py

from pydantic import BaseModel
from typing import List, Optional


class DocItem(BaseModel):
    department: str
    category: str
    subcategory: str
    summary: Optional[str] = None
    action_items: Optional[str] = None
    status: str
    destination_bucket: Optional[str] = None
    filename: str
    error_message: Optional[str] = None
    updated_at: str  # ISO 8601 format
    download_url: str  # e.g. "/documents/{id}/download"


class ClaimGroup(BaseModel):
    claim_number: str
    hierarchies: List[DocItem]


class PolicyGroup(BaseModel):
    policy_number: str
    hierarchies: List[DocItem]
    claims: List[ClaimGroup]


class AccountResponse(BaseModel):
    account_number: str
    policyholder_name: str
    policies: List[PolicyGroup]


class PolicyResponse(BaseModel):
    account_number: str
    policyholder_name: str
    policy: PolicyGroup


class ClaimResponse(BaseModel):
    account_number: str
    policyholder_name: str
    policy_number: str
    claim: ClaimGroup
