"""
Score Service

Handles URL scanning and phishing detection for PhishShield.

This service:
- Uses the ML engine to predict phishing probability
- Generates unique request IDs for tracking
- Updates application statistics
- Stores scan results in history
"""

import uuid
from datetime import datetime
from typing import Dict

from app.ml_engine.model import PhishDetector
from app.services import stats_service, storage_service

# Initialize the ML detector once at module load
_detector = PhishDetector()
"""Singleton instance of the phishing detection model"""


def scan_url(url: str) -> Dict:
    """
    Analyze a URL for phishing indicators using machine learning.
    
    This is the main business logic for URL scanning. It:
    1. Extracts features from the URL
    2. Runs ML model prediction
    3. Calculates phishing probability
    4. Updates global statistics
    5. Stores scan in history
    6. Returns structured result
    
    Args:
        url: The URL to analyze
        
    Returns:
        Dictionary containing:
            - url: The analyzed URL
            - phishing_probability: Score from 0.0 (safe) to 1.0 (phishing)
            - is_phishing: Boolean verdict (True if score > 0.60)
            - reasons: List of human-readable detection reasons
            - request_id: Unique identifier for this scan
            
    Example:
        >>> result = scan_url("http://paypa1-verify.xyz/login")
        >>> print(result)
        {
            "url": "http://paypa1-verify.xyz/login",
            "phishing_probability": 0.85,
            "is_phishing": True,
            "reasons": ["Suspicious Top-Level Domain (TLD)", ...],
            "request_id": "550e8400-e29b-41d4-a716-446655440000"
        }
    """
    # Run ML prediction
    prediction = _detector.predict(url)
    
    # Generate unique request ID
    request_id = str(uuid.uuid4())
    
    # Update statistics
    stats_service.increment_total_scans()
    if prediction["is_phishing"]:
        stats_service.increment_threats_blocked()
    
    # Create scan entry for history
    scan_entry = {
        "url": url,
        "status": "PHISHING" if prediction["is_phishing"] else "SAFE",
        "time": datetime.now().strftime("%I:%M:%S %p"),  # e.g., "02:30:45 PM"
        "score": prediction["score"],
        "reasons": prediction["reasons"]
    }
    
    # Store in recent scans history
    storage_service.add_scan(scan_entry)
    
    # Return result
    return {
        "url": url,
        "phishing_probability": prediction["score"],
        "is_phishing": prediction["is_phishing"],
        "reasons": prediction["reasons"],
        "request_id": request_id
    }


def get_recent_scans(limit: int = 50) -> list:
    """
    Retrieve recent scan history.
    
    Args:
        limit: Maximum number of scans to return (default: 50)
        
    Returns:
        List of recent scan entries
    """
    return storage_service.get_recent_scans(limit)
