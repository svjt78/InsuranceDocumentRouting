from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, UniqueConstraint, JSON
from sqlalchemy.sql import func
from .database import Base


class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    s3_key = Column(String, nullable=False)  # Key in storage
    extracted_text = Column(Text)
    department = Column(String)
    category = Column(String)
    subcategory = Column(String)
    summary = Column(Text)
    action_items = Column(Text)  # Could be JSON serialized later
    status = Column(String, default='pending')  # pending, processing, processed, failed, overridden, etc.
    destination_bucket = Column(String, nullable=True)
    destination_key = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    email_error = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


class Document1(Base):
    __tablename__ = 'documents1'
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    s3_key = Column(String, nullable=False)  # Key in AWS S3 storage
    extracted_text = Column(Text)
    department = Column(String)
    category = Column(String)
    subcategory = Column(String)
    summary = Column(Text)
    action_items = Column(Text)  # Could be JSON serialized later
    status = Column(String, default='pending')  # pending, processing, processed, failed, overridden, etc.
    destination_bucket = Column(String, nullable=True)
    destination_key = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    email_error = Column(Text, nullable=True)
    account_number = Column(String, nullable=True)
    policyholder_name = Column(String, nullable=True)
    policy_number = Column(String, nullable=True)
    claim_number = Column(String, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


class BucketMapping(Base):
    __tablename__ = 'bucket_mappings'
    id = Column(Integer, primary_key=True, index=True)
    bucket_name = Column(String, nullable=False)
    department = Column(String, nullable=False)
    category = Column(String, nullable=False)
    subcategory = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


class EmailSetting(Base):
    __tablename__ = 'email_settings'
    id = Column(Integer, primary_key=True, index=True)
    department = Column(String, nullable=False)
    email_addresses = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


class DocHierarchy(Base):
    __tablename__ = 'doc_hierarchy'
    id = Column(Integer, primary_key=True, index=True)
    department = Column(String, nullable=False)
    category = Column(String, nullable=False)
    subcategory = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    __table_args__ = (
        UniqueConstraint('department', 'category', 'subcategory'),
    )


class MessageOutbox(Base):
    __tablename__ = 'message_outbox'
    id = Column(Integer, primary_key=True, index=True)
    exchange = Column(String, nullable=False)
    routing_key = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    sent_at = Column(DateTime(timezone=True), nullable=True)
    error = Column(Text, nullable=True)
