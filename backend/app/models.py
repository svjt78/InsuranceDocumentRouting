from sqlalchemy import Column, Integer, String, Text, DateTime, UniqueConstraint
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

class BucketMapping(Base):
    __tablename__ = 'bucket_mappings'
    id = Column(Integer, primary_key=True, index=True)
    bucket_name = Column(String, nullable=False, unique=True)
    department = Column(String, nullable=False)
    category = Column(String, nullable=False)
    subcategory = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class EmailSetting(Base):
    __tablename__ = "email_settings"
    id = Column(Integer, primary_key=True, index=True)
    department = Column(String, nullable=False)
    email_addresses = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class DocHierarchy(Base):
    __tablename__ = "doc_hierarchy"
    id          = Column(Integer, primary_key=True, index=True)
    department  = Column(String, nullable=False)
    category    = Column(String, nullable=False)
    subcategory = Column(String, nullable=False)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint("department",
                                       "category",
                                       "subcategory"),)