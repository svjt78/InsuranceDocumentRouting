from typing import Optional
from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: int
    filename: str
    s3_key: str
    extracted_text: Optional[str] = None
    department: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    summary: Optional[str] = None
    action_items: Optional[str] = None
    status: str
    destination_bucket: Optional[str] = None
    destination_key: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        orm_mode = True


class Document1Out(DocumentOut):
    account_number: Optional[str] = None
    policyholder_name: Optional[str] = None
    policy_number: Optional[str] = None
    claim_number: Optional[str] = None

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
