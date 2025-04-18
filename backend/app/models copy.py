from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from .database import Base

class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    s3_key = Column(String, nullable=False)   # Key in minIO storage
    extracted_text = Column(Text)
    department = Column(String)
    category = Column(String)
    subcategory = Column(String)
    summary = Column(Text)
    action_items = Column(Text)  # Could be JSON serialized later
    status = Column(String, default='pending')  # pending, processing, processed, failed, overridden
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
