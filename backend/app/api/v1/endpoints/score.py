from fastapi import APIRouter, HTTPException
from app.schemas.score import ScoreRequest, ScoreResponse
import uuid
import random
from datetime import datetime
from typing import List

router = APIRouter()

# In-memory storage for recent scans (Lite Mode)
recent_scans: List[dict] = []
TOTAL_SCANS = 0
THREATS_BLOCKED = 0

from app.ml_engine.model import PhishDetector

detector = PhishDetector()

@router.post("/score", response_model=ScoreResponse)
async def score_url(request: ScoreRequest):
    # Use the ML Engine for prediction
    prediction = detector.predict(request.url)
    
    result = ScoreResponse(
        url=request.url,
        phishing_probability=prediction["score"],
        is_phishing=prediction["is_phishing"],
        reasons=prediction["reasons"],
        request_id=str(uuid.uuid4())
    )
    
    # Update global stats
    global TOTAL_SCANS, THREATS_BLOCKED
    TOTAL_SCANS += 1
    if prediction["is_phishing"]:
        THREATS_BLOCKED += 1

    # Store in recent scans
    scan_entry = {
        "url": request.url,
        "status": "PHISHING" if prediction["is_phishing"] else "SAFE",
        "time": datetime.now().strftime("%I:%M:%S %p"),
        "score": prediction["score"],
        "reasons": prediction["reasons"]
    }
    recent_scans.insert(0, scan_entry)
    if len(recent_scans) > 50:  # Keep last 50
        recent_scans.pop()
        
    return result

@router.get("/score/recent")
async def get_recent_scans():
    return recent_scans
