"""
PhishShield AI - URL Scoring Endpoint

This module provides the core phishing detection API endpoint.
It receives URLs from the browser extension or dashboard, analyzes them
using the score service, and returns a phishing probability score.

Endpoints:
    POST /api/v1/score - Analyze a URL for phishing indicators
    GET /api/v1/score/recent - Retrieve recent scan history

Author: PhishShield Team
"""

from fastapi import APIRouter, HTTPException
from app.schemas.score import ScoreRequest, ScoreResponse
from app.services import score_service

# Initialize FastAPI router for score-related endpoints
router = APIRouter()


@router.post("/score", response_model=ScoreResponse)
async def score_url(request: ScoreRequest):
    """
    Analyze a URL for phishing indicators using machine learning.
    
    This is the main endpoint used by the browser extension to check URLs
    in real-time before the user visits them. The request is forwarded to
    the score service which handles all business logic.
    
    Args:
        request: ScoreRequest containing the URL to analyze
        
    Returns:
        ScoreResponse with:
            - url: The analyzed URL
            - phishing_probability: Score from 0.0 (safe) to 1.0 (phishing)
            - is_phishing: Boolean verdict (True if score > 0.60)
            - reasons: List of human-readable detection reasons
            - request_id: Unique identifier for this scan
            
    Example Request:
        POST /api/v1/score
        {
            "url": "http://paypa1-verify.xyz/login"
        }
        
    Example Response:
        {
            "url": "http://paypa1-verify.xyz/login",
            "phishing_probability": 0.85,
            "is_phishing": true,
            "reasons": [
                "Suspicious Top-Level Domain (TLD)",
                "Sensitive keywords found in URL"
            ],
            "request_id": "550e8400-e29b-41d4-a716-446655440000"
        }
    """
    try:
        # Delegate to score service for business logic
        result = score_service.scan_url(request.url)
        
        # Convert to response model
        return ScoreResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error scanning URL: {str(e)}"
        )


@router.get("/score/recent")
async def get_recent_scans():
    """
    Retrieve the history of recent URL scans.
    
    Returns the last 50 scanned URLs with their results, displayed in
    the dashboard for real-time monitoring. Scans are ordered from most
    recent to oldest.
    
    This endpoint is polled by the dashboard every few seconds to show
    live activity.
    
    Returns:
        List of scan entries, each containing:
            - url: The scanned URL
            - status: "SAFE" or "PHISHING"
            - time: Timestamp of the scan (HH:MM:SS AM/PM)
            - score: Phishing probability (0.0 - 1.0)
            - reasons: List of detection reasons
            
    Example Response:
        [
            {
                "url": "http://evil-site.xyz",
                "status": "PHISHING",
                "time": "02:30:45 PM",
                "score": 0.92,
                "reasons": ["Suspicious TLD", "IP address used"]
            },
            {
                "url": "https://google.com",
                "status": "SAFE",
                "time": "02:29:12 PM",
                "score": 0.05,
                "reasons": []
            }
        ]
    """
    try:
        # Delegate to score service
        return score_service.get_recent_scans()
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving recent scans: {str(e)}"
        )
