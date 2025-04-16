from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models, database

# Define the router WITHOUT a prefix
router = APIRouter(tags=["Lookup"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=dict)
def get_document_hierarchy(db: Session = Depends(get_db)):
    rows = db.query(models.DocHierarchy).all()
    hierarchy = {}
    for row in rows:
        dept = hierarchy.setdefault(row.department, {})
        cat = dept.setdefault(row.category, [])
        if row.subcategory not in cat:
            cat.append(row.subcategory)
    return hierarchy
