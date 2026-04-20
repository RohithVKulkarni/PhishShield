"""
Score Service

Handles URL scanning and phishing detection for PhishShield.

This service:
- Uses the ML engine to predict phishing probability
- Runs HTML content analysis for an additional phishing signal
- Blends ML score (70%) with HTML analysis score (30%)
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
from app.services.html_analyzer import analyze_html
from sqlalchemy.orm import Session

# Initialize the ML detector once at module load
_detector = PhishDetector()
"""Singleton instance of the phishing detection model"""


def scan_url(url: str, html_content: Optional[str] = None, db: Optional[Session] = None) -> Dict:
    """
    Analyze a URL for phishing indicators using machine learning.
    
    This is the main business logic for URL scanning. It:
    1. Checks whitelist/blacklist (if database available)
    2. Extracts features from the URL
    3. Runs ML model prediction
    4. Runs HTML content analysis (if html_content provided or URL reachable)
    5. Blends ML score (70%) with HTML score (30%) into final probability
    6. Updates global statistics
    7. Stores scan in history
    8. Returns structured result

    Args:
        url: The URL to analyze
        html_content: Optional raw HTML string from the browser extension.
                      If provided, HTML analysis runs without extra HTTP request.
        db: Optional database session for whitelist/blacklist checking

    Returns:
        Dictionary containing:
            - url: The analyzed URL
            - phishing_probability: Blended score 0.0 (safe) to 1.0 (phishing)
            - is_phishing: Boolean verdict (True if final score > 0.60)
            - reasons: List of human-readable detection reasons
            - request_id: Unique identifier for this scan
            - html_score: HTML-only analysis score (None if unavailable)
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
                    "request_id": request_id,
                    "scan_time": datetime.utcnow().isoformat()
                }
            
            elif list_match["list_type"] == "blacklist":
                # Blacklisted - immediately return phishing
                request_id = str(uuid.uuid4())
                stats_service.increment_total_scans()
                stats_service.increment_threats_blocked()
                
                reasons = [f"[FAIL] Blacklisted by user: {list_match['pattern']}"]
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
                    "request_id": request_id,
                    "scan_time": datetime.utcnow().isoformat()
                }
    
    # No list match - proceed with ML prediction
    # Run ML prediction (URL-based features)
    prediction = _detector.predict(url)
    ml_score = prediction["score"]
    reasons = list(prediction["reasons"])

    # --- HTML Content Analysis ---
    # Run HTML analysis when html_content is provided by the extension OR
    # when no html_content is given (analyzer will attempt to fetch the page).
    # The analyzer returns quickly with score=0.0 if the page can't be reached.
    html_result = analyze_html(url, html_content=html_content)
    html_score = html_result.get("html_score", 0.0)
    html_reasons = html_result.get("html_reasons", [])

    # Append HTML-derived reasons (avoid duplicates)
    for r in html_reasons:
        if r not in reasons:
            reasons.append(r)

    # Blend scores: ML carries 70% weight, HTML carries 30%
    # This keeps ML as the primary signal while HTML boosts detection.
    if html_score > 0.0:
        final_score = round(min(ml_score * 0.7 + html_score * 0.3, 1.0), 4)
    else:
        final_score = round(ml_score, 4)  # HTML unavailable — use ML score as-is

    is_phishing = final_score > 0.60

    # Generate unique request ID
    request_id = str(uuid.uuid4())

    # Update statistics
    stats_service.increment_total_scans()
    if is_phishing:
        stats_service.increment_threats_blocked()

    # Create scan entry for history
    scan_entry = {
        "url": url,
        "status": "PHISHING" if is_phishing else "SAFE",
        "time": datetime.now().strftime("%I:%M:%S %p"),  # e.g., "02:30:45 PM"
        "score": final_score,
        "reasons": reasons
    }

    # Store in recent scans history
    storage_service.add_scan(scan_entry)

    # Return result
    return {
        "url": url,
        "phishing_probability": final_score,
        "is_phishing": is_phishing,
        "reasons": reasons,
        "request_id": request_id,
        "html_score": html_score if html_score > 0.0 else None
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
