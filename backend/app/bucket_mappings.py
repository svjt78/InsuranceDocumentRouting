from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from .database import SessionLocal
from . import models

# Pydantic schemas for BucketMapping

class BucketMappingBase(BaseModel):
    bucket_name: str
    department: str
    category: str
    subcategory: str

class BucketMappingCreate(BucketMappingBase):
    pass

class BucketMappingUpdate(BaseModel):
    bucket_name: Optional[str] = None
    department: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None

class BucketMappingOut(BucketMappingBase):
    id: int
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        orm_mode = True

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Define the router with an appropriate prefix
router = APIRouter(prefix="/bucket-mappings", tags=["Bucket Mappings"])

@router.get("/", response_model=List[BucketMappingOut])
def read_bucket_mappings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve all bucket mappings with optional pagination.
    """
    mappings = db.query(models.BucketMapping).offset(skip).limit(limit).all()
    return mappings

@router.post("/", response_model=BucketMappingOut)
def create_bucket_mapping(mapping: BucketMappingCreate, db: Session = Depends(get_db)):
    """
    Create a new bucket mapping.
    """
    # Check for existing bucket mapping by bucket_name to avoid duplicates
    existing_mapping = db.query(models.BucketMapping).filter(
        models.BucketMapping.bucket_name == mapping.bucket_name
    ).first()
    if existing_mapping:
        raise HTTPException(status_code=400, detail="Bucket mapping already exists")
    new_mapping = models.BucketMapping(**mapping.dict())
    db.add(new_mapping)
    db.commit()
    db.refresh(new_mapping)
    return new_mapping

@router.put("/{mapping_id}", response_model=BucketMappingOut)
def update_bucket_mapping(mapping_id: int, mapping: BucketMappingUpdate, db: Session = Depends(get_db)):
    """
    Update an existing bucket mapping.
    """
    db_mapping = db.query(models.BucketMapping).filter(models.BucketMapping.id == mapping_id).first()
    if not db_mapping:
        raise HTTPException(status_code=404, detail="Bucket mapping not found")
    update_data = mapping.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_mapping, key, value)
    db.commit()
    db.refresh(db_mapping)
    return db_mapping

@router.delete("/{mapping_id}")
def delete_bucket_mapping(mapping_id: int, db: Session = Depends(get_db)):
    """
    Delete a bucket mapping by ID.
    """
    db_mapping = db.query(models.BucketMapping).filter(models.BucketMapping.id == mapping_id).first()
    if not db_mapping:
        raise HTTPException(status_code=404, detail="Bucket mapping not found")
    db.delete(db_mapping)
    db.commit()
    return {"message": "Bucket mapping deleted successfully", "id": mapping_id}
