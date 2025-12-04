from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import ScanResult
import random

router = APIRouter()

@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    total_scans = db.query(ScanResult).count()
    threats_blocked = db.query(ScanResult).filter(ScanResult.is_phishing == True).count()
    
    return {
        "total_scans": total_scans,
        "threats_neutralized": threats_blocked,
        "active_nodes": 49, # Mock for now
        "latency": random.randint(20, 45) # Mock latency
    }
