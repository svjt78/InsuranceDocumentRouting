# backend/app/schemas.py

from pydantic import BaseModel

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
