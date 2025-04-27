# backend/app/routes/doc_hierarchy.py

import io
import csv
import json
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, database

router = APIRouter(
    prefix="/doc-hierarchy",
    tags=["Lookup"],
)


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------------------------------------------------
# Pydantic schemas
# -------------------------------------------------------------------

class HierarchyBase(BaseModel):
    department: str
    category: str
    subcategory: str

class HierarchyCreate(HierarchyBase):
    pass

class HierarchyUpdate(BaseModel):
    department:  Optional[str] = None
    category:    Optional[str] = None
    subcategory: Optional[str] = None

class HierarchyOut(HierarchyBase):
    id: int

    class Config:
        orm_mode = True


# -------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------

@router.get("/all", response_model=List[HierarchyOut])
def get_all_nodes(db: Session = Depends(get_db)):
    """
    Return every doc_hierarchy row (flat list with IDs).
    """
    return db.query(models.DocHierarchy).all()


@router.get("/", response_model=Dict[str, Dict[str, List[str]]])
def get_tree(db: Session = Depends(get_db)):
    """
    Nested hierarchy:
      {
        department1: { categoryA: [sub1, sub2], … },
        department2: { … },
      }
    """
    rows = db.query(models.DocHierarchy).all()
    hierarchy: Dict[str, Dict[str, List[str]]] = {}
    for row in rows:
        dept = hierarchy.setdefault(row.department, {})
        cat  = dept.setdefault(row.category, [])
        if row.subcategory not in cat:
            cat.append(row.subcategory)
    return hierarchy


@router.post("/", response_model=HierarchyOut, status_code=status.HTTP_201_CREATED)
def create_node(node: HierarchyCreate, db: Session = Depends(get_db)):
    """
    Add a new department/category/subcategory triple.
    """
    rec = models.DocHierarchy(**node.dict())
    db.add(rec)
    try:
        db.commit()
        db.refresh(rec)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate hierarchy entry"
        )
    return rec


@router.put("/{node_id}", response_model=HierarchyOut)
def update_node(
    node_id: int,
    node: HierarchyUpdate,
    db: Session = Depends(get_db),
):
    """
    Rename department, category, or subcategory of a single entry by ID.
    """
    rec = db.query(models.DocHierarchy).filter(models.DocHierarchy.id == node_id).first()
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")

    update_data = node.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rec, field, value)

    try:
        db.commit()
        db.refresh(rec)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Update would create a duplicate entry"
        )
    return rec


@router.delete("/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_node(node_id: int, db: Session = Depends(get_db)):
    """
    Delete a single hierarchy entry by ID.
    """
    rec = db.query(models.DocHierarchy).filter(models.DocHierarchy.id == node_id).first()
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")
    db.delete(rec)
    db.commit()


@router.get("/export")
def export_tree(
    format: str = "json",
    db: Session = Depends(get_db),
):
    """
    Export the hierarchy as JSON or CSV.
    """
    rows = db.query(models.DocHierarchy).all()

    if format == "json":
        return [
            {"department": r.department, "category": r.category, "subcategory": r.subcategory}
            for r in rows
        ]

    elif format == "csv":
        def stream_csv():
            buf = io.StringIO()
            writer = csv.writer(buf)
            writer.writerow(["department", "category", "subcategory"])
            for r in rows:
                writer.writerow([r.department, r.category, r.subcategory])
            yield buf.getvalue()

        return StreamingResponse(
            stream_csv(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=doc_hierarchy.csv"}
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported export format"
        )


@router.post("/import")
async def import_tree(
    file: UploadFile = File(...),
    merge: bool = True,
    db: Session = Depends(get_db),
):
    """
    Import hierarchy from JSON or CSV.
      - merge=True: skip duplicates.
    """
    content = await file.read()
    imported = skipped = 0

    # JSON import
    if file.filename.lower().endswith(".json"):
        try:
            items = json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON file")
        for item in items:
            rec = models.DocHierarchy(**item)
            db.add(rec)
            try:
                db.commit()
                imported += 1
            except IntegrityError:
                db.rollback()
                skipped += 1

    # CSV import
    elif file.filename.lower().endswith(".csv"):
        text = content.decode("utf-8")
        reader = csv.DictReader(io.StringIO(text))
        for row in reader:
            rec = models.DocHierarchy(
                department = row["department"],
                category   = row["category"],
                subcategory= row["subcategory"]
            )
            db.add(rec)
            try:
                db.commit()
                imported += 1
            except IntegrityError:
                db.rollback()
                skipped += 1

    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")

    return {"imported": imported, "skipped": skipped}
