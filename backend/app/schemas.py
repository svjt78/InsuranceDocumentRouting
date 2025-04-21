# backend/app/schemas.py

from pydantic import BaseModel

class DocumentOut(BaseModel):
    id: int
    filename: str
    s3_key: str
    extracted_text: str = None
    department: str = None
    category: str = None
    subcategory: str = None
    summary: str = None
    action_items: str = None
    status: str
    destination_bucket: str = None
    destination_key: str = None
    error_message: str = None

    class Config:
        orm_mode = True

class EmailSettingBase(BaseModel):
    department: str
    email_addresses: str   # Comma-separated list

class EmailSettingCreate(EmailSettingBase):
    pass

class EmailSettingUpdate(EmailSettingBase):
    pass

class EmailSettingOut(EmailSettingBase):
    id: int

    class Config:
        orm_mode = True
