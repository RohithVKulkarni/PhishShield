"""
Storage Service

Manages in-memory data storage for PhishShield.
In production, this should be replaced with database storage.

This service maintains:
- Recent scan history (last 50 scans)
"""

from typing import List, Dict
from threading import Lock

# Thread-safe lock for concurrent access
_lock = Lock()

# In-memory storage
_recent_scans: List[Dict] = []
"""List of recent URL scans for dashboard display"""


def add_scan(scan_entry: Dict) -> None:
    """
    Add a scan entry to the recent scans history.
    
    Maintains a maximum of 50 entries, removing the oldest when limit is reached.
    Thread-safe for concurrent requests.
    
    Args:
        scan_entry: Dictionary containing scan details:
            - url: The scanned URL
            - status: "SAFE" or "PHISHING"
            - time: Timestamp string (HH:MM:SS AM/PM)
            - score: Phishing probability (0.0 - 1.0)
            - reasons: List of detection reasons
    """
    with _lock:
        # Add to beginning of list (most recent first)
        _recent_scans.insert(0, scan_entry)
        
        # Maintain maximum of 50 entries
        if len(_recent_scans) > 50:
            _recent_scans.pop()


def get_recent_scans(limit: int = 50) -> List[Dict]:
    """
    Retrieve recent scan history.
    
    Args:
        limit: Maximum number of scans to return (default: 50)
        
    Returns:
        List of scan entries, ordered from most recent to oldest
    """
    with _lock:
        return _recent_scans[:limit]


def clear_scans() -> None:
    """
    Clear all scan history.
    
    Useful for testing or manual cleanup.
    """
    with _lock:
        _recent_scans.clear()


def get_scan_count() -> int:
    """
    Get the current number of scans in history.
    
    Returns:
        Number of scans currently stored
    """
    with _lock:
        return len(_recent_scans)
