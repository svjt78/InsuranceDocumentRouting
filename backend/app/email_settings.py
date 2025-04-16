from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from .database import SessionLocal
from . import models, schemas

# Create the router WITHOUT a prefix so that main.py's include_router determines the effective path.
router = APIRouter(tags=["Email Settings"])
logger = logging.getLogger("email_settings")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[schemas.EmailSettingOut])
def get_email_settings(db: Session = Depends(get_db)):
    """Retrieve all email settings."""
    settings = db.query(models.EmailSetting).all()
    return settings

@router.post("/", response_model=schemas.EmailSettingOut)
def create_email_setting(setting_data: schemas.EmailSettingCreate, db: Session = Depends(get_db)):
    """Create a new email setting."""
    email_setting = models.EmailSetting(
        department=setting_data.department,
        email_addresses=setting_data.email_addresses
    )
    db.add(email_setting)
    try:
        db.commit()
        db.refresh(email_setting)
        return email_setting
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating email setting: {e}")
        raise HTTPException(status_code=500, detail="Error creating email setting")

@router.put("/{setting_id}", response_model=schemas.EmailSettingOut)
def update_email_setting(setting_id: int, update_data: schemas.EmailSettingUpdate, db: Session = Depends(get_db)):
    """Update an existing email setting."""
    setting = db.query(models.EmailSetting).filter(models.EmailSetting.id == setting_id).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Email setting not found")
    setting.department = update_data.department
    setting.email_addresses = update_data.email_addresses
    try:
        db.commit()
        db.refresh(setting)
        return setting
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating email setting {setting_id}: {e}")
        raise HTTPException(status_code=500, detail="Error updating email setting")

@router.delete("/{setting_id}")
def delete_email_setting(setting_id: int, db: Session = Depends(get_db)):
    """Delete an email setting."""
    setting = db.query(models.EmailSetting).filter(models.EmailSetting.id == setting_id).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Email setting not found")
    try:
        db.delete(setting)
        db.commit()
        return {"message": "Email setting deleted"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting email setting {setting_id}: {e}")
        raise HTTPException(status_code=500, detail="Error deleting email setting")
