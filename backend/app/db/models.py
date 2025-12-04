from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from .database import Base
from datetime import datetime

class ScanResult(Base):
    __tablename__ = "scan_results"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    status = Column(String) # "PHISHING" or "SAFE"
    score = Column(Float)
    is_phishing = Column(Boolean)
    reasons = Column(String) # Stored as comma-separated string or JSON string
    timestamp = Column(DateTime, default=datetime.now)
