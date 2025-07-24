"""
This module centralizes document hierarchy fetching and grouping logic for the Insurance Doc Routing app.
Provides functions to fetch documents by account, policy, or claim, and to build nested hierarchies suitable for API responses.
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from ..models import Document1


def fetch_docs_by_account(db: Session, acct: str) -> List[Document1]:
    """
    Retrieve all Document1 records matching the given account number.
    """
    return db.query(Document1).filter(Document1.account_number == acct).all()


def fetch_docs_by_policy(db: Session, pol: str) -> List[Document1]:
    """
    Retrieve all Document1 records matching the given policy number.
    """
    return db.query(Document1).filter(Document1.policy_number == pol).all()


def fetch_docs_by_claim(db: Session, clm: str) -> List[Document1]:
    """
    Retrieve all Document1 records matching the given claim number.
    """
    return db.query(Document1).filter(Document1.claim_number == clm).all()


def _build_doc_item(d: Document1) -> Dict[str, Any]:
    """
    Helper to construct a document item dict with all metadata and download URL.
    Omits optional fields when they are None (e.g., claim_number).
    """
    item: Dict[str, Any] = {
        "account_number": d.account_number,
        "policyholder_name": d.policyholder_name,
        "policy_number": d.policy_number,
        "department": d.department,
        "category": d.category,
        "subcategory": d.subcategory,
        "summary": d.summary,
        "action_items": d.action_items,        # single delimited string
        "status": d.status,
        "destination_bucket": d.destination_bucket,
        "error_message": d.error_message,
        "updated_at": d.updated_at.isoformat() if d.updated_at else None,
        "filename": d.filename,
        "download_url": f"/documents/{d.id}/download"
    }

    # Omit claim_number if not present
    if d.claim_number:
        item["claim_number"] = d.claim_number

    return item


def build_account_hierarchy(docs: List[Document1]) -> Dict[str, Any]:
    """
    Build a hierarchical structure for an account:
      - account_number
      - policyholder_name
      - policies: List of policies, each containing:
          * policy_number
          * hierarchies: List of docs under the policy (non-claims)
          * claims: List of claim groups under the policy
    """
    if not docs:
        return {"account_number": None, "policyholder_name": None, "policies": []}

    account_number = docs[0].account_number
    policyholder_name = docs[0].policyholder_name

    # Group documents by policy number
    policies: Dict[str, List[Document1]] = {}
    for d in docs:
        policies.setdefault(d.policy_number, []).append(d)

    policy_list: List[Dict[str, Any]] = []
    for policy_num, policy_docs in policies.items():
        # Separate policy-level docs (non-claims)
        policy_docs_non_claims = [d for d in policy_docs if d.department != 'Claims']
        policy_docs_sorted = sorted(
            policy_docs_non_claims,
            key=lambda d: d.updated_at or d.created_at,
            reverse=True
        )
        hierarchies = [_build_doc_item(d) for d in policy_docs_sorted]

        # Group claim docs under this policy
        claim_groups: Dict[str, List[Document1]] = {}
        for d in policy_docs:
            if d.department == 'Claims' and d.claim_number:
                claim_groups.setdefault(d.claim_number, []).append(d)

        claim_list: List[Dict[str, Any]] = []
        for claim_num, claim_docs in claim_groups.items():
            claim_docs_sorted = sorted(
                claim_docs,
                key=lambda d: d.updated_at or d.created_at,
                reverse=True
            )
            claim_list.append({
                "claim_number": claim_num,
                "hierarchies": [_build_doc_item(d) for d in claim_docs_sorted]
            })

        policy_list.append({
            "policy_number": policy_num,
            "hierarchies": hierarchies,
            "claims": claim_list
        })

    return {
        "account_number": account_number,
        "policyholder_name": policyholder_name,
        "policies": policy_list
    }


def build_policy_hierarchy(docs: List[Document1]) -> Dict[str, Any]:
    """
    Build a hierarchical structure for a single policy:
      - account_number
      - policyholder_name
      - policy: Dict containing:
          * policy_number
          * hierarchies: List of docs under this policy (non-claims)
          * claims: List of claim groups under this policy
    """
    if not docs:
        return {
            "account_number": None,
            "policyholder_name": None,
            "policy": {"policy_number": None, "hierarchies": [], "claims": []}
        }

    account_number = docs[0].account_number
    policyholder_name = docs[0].policyholder_name
    policy_number = docs[0].policy_number

    # Policy-level docs
    policy_docs_non_claims = [d for d in docs if d.department != 'Claims']
    policy_docs_sorted = sorted(
        policy_docs_non_claims,
        key=lambda d: d.updated_at or d.created_at,
        reverse=True
    )
    hierarchies = [_build_doc_item(d) for d in policy_docs_sorted]

    # Claims under this policy
    claim_groups: Dict[str, List[Document1]] = {}
    for d in docs:
        if d.department == 'Claims' and d.claim_number:
            claim_groups.setdefault(d.claim_number, []).append(d)

    claim_list: List[Dict[str, Any]] = []
    for claim_num, claim_docs in claim_groups.items():
        claim_docs_sorted = sorted(
            claim_docs,
            key=lambda d: d.updated_at or d.created_at,
            reverse=True
        )
        claim_list.append({
            "claim_number": claim_num,
            "hierarchies": [_build_doc_item(d) for d in claim_docs_sorted]
        })

    return {
        "account_number": account_number,
        "policyholder_name": policyholder_name,
        "policy": {
            "policy_number": policy_number,
            "hierarchies": hierarchies,
            "claims": claim_list
        }
    }


def build_claim_hierarchy(docs: List[Document1]) -> Dict[str, Any]:
    """
    Build a hierarchical structure for a single claim:
      - account_number
      - policyholder_name
      - policy_number
      - claim: Dict containing:
          * claim_number
          * hierarchies: List of docs under this claim
    """
    if not docs:
        return {
            "account_number": None,
            "policyholder_name": None,
            "policy_number": None,
            "claim": {"claim_number": None, "hierarchies": []}
        }

    account_number = docs[0].account_number
    policyholder_name = docs[0].policyholder_name
    policy_number = docs[0].policy_number
    claim_number = docs[0].claim_number

    # Claim docs
    claim_docs_sorted = sorted(
        docs,
        key=lambda d: d.updated_at or d.created_at,
        reverse=True
    )
    hierarchies = [_build_doc_item(d) for d in claim_docs_sorted]

    return {
        "account_number": account_number,
        "policyholder_name": policyholder_name,
        "policy_number": policy_number,
        "claim": {
            "claim_number": claim_number,
            "hierarchies": hierarchies
        }
    }
