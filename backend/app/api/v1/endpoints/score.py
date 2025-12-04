from fastapi import APIRouter, HTTPException, Depends
from app.schemas.score import ScoreRequest, ScoreResponse
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import ScanResult
from app.ml_engine.model import PhishDetector

router = APIRouter()
detector = PhishDetector()

@router.post("/score", response_model=ScoreResponse)
async def score_url(request: ScoreRequest, db: Session = Depends(get_db)):
    # Use the ML Engine for prediction
    prediction = detector.predict(request.url)
    
    result = ScoreResponse(
        url=request.url,
        phishing_probability=prediction["score"],
        is_phishing=prediction["is_phishing"],
        reasons=prediction["reasons"],
        request_id=str(uuid.uuid4())
    )
    
    # Store in database
    scan_entry = ScanResult(
        url=request.url,
        status="PHISHING" if prediction["is_phishing"] else "SAFE",
        score=prediction["score"],
        is_phishing=prediction["is_phishing"],
        reasons=",".join(prediction["reasons"]) if prediction["reasons"] else "",
        timestamp=datetime.now()
    )
    db.add(scan_entry)
    db.commit()
    db.refresh(scan_entry)
        
    return result

@router.get("/score/recent")
async def get_recent_scans(db: Session = Depends(get_db)):
    scans = db.query(ScanResult).order_by(ScanResult.timestamp.desc()).limit(50).all()
    
    # Format for frontend
    formatted_scans = []
    for scan in scans:
        formatted_scans.append({
            "url": scan.url,
            "status": scan.status,
            "time": scan.timestamp.strftime("%I:%M:%S %p"),
            "score": scan.score,
            "reasons": scan.reasons.split(",") if scan.reasons else []
        })
    return formatted_scans
