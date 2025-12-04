"""
Statistics Service

Manages application-wide statistics for PhishShield.

Tracks:
- Total number of URLs scanned
- Total number of phishing threats blocked
- Active nodes (mock data)
- System latency (mock data)
"""

import random
from threading import Lock
from typing import Dict

# Thread-safe lock for concurrent access
_lock = Lock()

# Global statistics counters
_total_scans: int = 0
"""Total number of URLs scanned since server started"""

_threats_blocked: int = 0
"""Total number of phishing URLs detected since server started"""


def increment_total_scans() -> None:
    """
    Increment the total scans counter.
    
    Thread-safe for concurrent requests.
    """
    global _total_scans
    with _lock:
        _total_scans += 1


def increment_threats_blocked() -> None:
    """
    Increment the threats blocked counter.
    
    Thread-safe for concurrent requests.
    """
    global _threats_blocked
    with _lock:
        _threats_blocked += 1


def get_stats() -> Dict:
    """
    Get current application statistics.
    
    Returns:
        Dictionary containing:
            - total_scans: Total URLs scanned
            - threats_neutralized: Total phishing URLs blocked
            - active_nodes: Number of active detection nodes (mock)
            - latency: System latency in ms (mock)
    """
    with _lock:
        return {
            "total_scans": _total_scans,
            "threats_neutralized": _threats_blocked,
            "active_nodes": 49,  # Mock value for dashboard
            "latency": random.randint(20, 45)  # Mock latency in ms
        }


def get_total_scans() -> int:
    """
    Get the total number of scans.
    
    Returns:
        Total scans count
    """
    with _lock:
        return _total_scans


def get_threats_blocked() -> int:
    """
    Get the total number of threats blocked.
    
    Returns:
        Threats blocked count
    """
    with _lock:
        return _threats_blocked


def reset_stats() -> None:
    """
    Reset all statistics to zero.
    
    Useful for testing or manual reset.
    """
    global _total_scans, _threats_blocked
    with _lock:
        _total_scans = 0
        _threats_blocked = 0
