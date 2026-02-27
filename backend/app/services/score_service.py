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
from typing import Dict, Optional

from app.ml_engine.model import PhishDetector
from app.services import stats_service, storage_service
from app.services.user_list_service import UserListService
from sqlalchemy.orm import Session

# Initialize the ML detector once at module load
_detector = PhishDetector()
"""Singleton instance of the phishing detection model"""


def scan_url(url: str, db: Optional[Session] = None) -> Dict:
    """
    Analyze a URL for phishing indicators using machine learning.
    
    This is the main business logic for URL scanning. It:
    1. Checks whitelist/blacklist (if database available)
    2. Extracts features from the URL
    3. Runs ML model prediction
    4. Calculates phishing probability
    5. Updates global statistics
    6. Stores scan in history
    7. Returns structured result
    
    Args:
        url: The URL to analyze
        db: Optional database session for whitelist/blacklist checking
        
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
    # Check whitelist/blacklist first (if database available)
    if db is not None:
        list_match = UserListService.check_url(db, url)
        if list_match:
            if list_match["list_type"] == "whitelist":
                # Whitelisted - immediately return safe
                request_id = str(uuid.uuid4())
                stats_service.increment_total_scans()
                
                reasons = [f"✓ Whitelisted by user: {list_match['pattern']}"]
                if list_match.get("note"):
                    reasons.append(f"Note: {list_match['note']}")
                
                scan_entry = {
                    "url": url,
                    "status": "SAFE",
                    "time": datetime.now().strftime("%I:%M:%S %p"),
                    "score": 0.0,
                    "reasons": reasons
                }
                storage_service.add_scan(scan_entry)
                
                return {
                    "url": url,
                    "phishing_probability": 0.0,
                    "is_phishing": False,
                    "reasons": reasons,
                    "request_id": request_id
                }
            
            elif list_match["list_type"] == "blacklist":
                # Blacklisted - immediately return phishing
                request_id = str(uuid.uuid4())
                stats_service.increment_total_scans()
                stats_service.increment_threats_blocked()
                
                reasons = [f"⚠ Blacklisted by user: {list_match['pattern']}"]
                if list_match.get("note"):
                    reasons.append(f"Note: {list_match['note']}")
                
                scan_entry = {
                    "url": url,
                    "status": "PHISHING",
                    "time": datetime.now().strftime("%I:%M:%S %p"),
                    "score": 1.0,
                    "reasons": reasons
                }
                storage_service.add_scan(scan_entry)
                
                return {
                    "url": url,
                    "phishing_probability": 1.0,
                    "is_phishing": True,
                    "reasons": reasons,
                    "request_id": request_id
                }
    
    # No list match - proceed with ML prediction
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
