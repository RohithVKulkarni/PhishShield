"""
Database Models for PhishShield

Defines SQLAlchemy ORM models for:
- UserList: Whitelist and blacklist entries
- ScanHistory: Persistent scan history
- Feedback: User feedback for active learning (future use)
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ListType(str, enum.Enum):
    """Enum for list types"""
    WHITELIST = "whitelist"
    BLACKLIST = "blacklist"


class UserList(Base):
    """
    User-defined whitelist and blacklist entries.
    
    Stores URLs or domain patterns that users want to always allow or block.
    Supports wildcard patterns for flexible matching.
    """
    __tablename__ = "user_lists"

    id = Column(Integer, primary_key=True, index=True)
    list_type = Column(Enum(ListType), nullable=False, index=True)
    
    # URL or domain pattern (e.g., "example.com", "*.example.com", "http://specific-page.com")
    pattern = Column(String(500), nullable=False, index=True)
    
    # Optional user note/reason for adding this entry
    note = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Future: user_id for multi-user support
    # user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    def __repr__(self):
        return f"<UserList(type={self.list_type}, pattern={self.pattern})>"


class ScanHistory(Base):
    """
    Persistent storage for URL scan history.
    
    Replaces the in-memory storage_service with database persistence.
    """
    __tablename__ = "scan_history"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(2000), nullable=False, index=True)
    
    # Scan result
    status = Column(String(20), nullable=False)  # "SAFE" or "PHISHING"
    score = Column(Float, nullable=False)  # Phishing probability (0.0 - 1.0)
    
    # Detection reasons (stored as JSON string)
    reasons = Column(Text, nullable=True)
    
    # Timestamp
    scanned_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Request tracking
    request_id = Column(String(36), nullable=True, index=True)  # UUID
    
    # Source of detection (e.g., "ml_model", "whitelist", "blacklist", "threat_intel")
    detection_source = Column(String(50), nullable=True)

    def __repr__(self):
        return f"<ScanHistory(url={self.url[:50]}, status={self.status})>"


class Feedback(Base):
    """
    User feedback for active learning pipeline.
    
    Stores user corrections and comments to improve the ML model.
    """
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(2000), nullable=False, index=True)
    
    # User's verdict
    is_phishing = Column(Boolean, nullable=False)
    
    # Optional user comment
    user_comment = Column(Text, nullable=True)
    
    # Original prediction (for comparison)
    original_prediction = Column(Boolean, nullable=True)
    original_score = Column(Float, nullable=True)
    
    # Timestamp
    submitted_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Whether this feedback has been used in model retraining
    used_in_training = Column(Boolean, default=False, index=True)

    def __repr__(self):
        return f"<Feedback(url={self.url[:50]}, is_phishing={self.is_phishing})>"
