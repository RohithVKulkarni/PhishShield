"""
PhishShield AI - Statistics Endpoint

This module provides application statistics for the dashboard.

Endpoints:
    GET /api/v1/stats - Retrieve application statistics

Author: PhishShield Team
"""

from fastapi import APIRouter, HTTPException
from app.services import stats_service

router = APIRouter()


@router.get("/stats")
async def get_stats():
    """
    Retrieve application statistics.
    
    Returns current statistics including:
    - Total URLs scanned
    - Total phishing threats blocked
    - Active detection nodes
    - System latency
    
    Returns:
        Dictionary containing application statistics
        
    Example Response:
        {
            "total_scans": 1523,
            "threats_neutralized": 47,
            "active_nodes": 49,
            "latency": 32
        }
    """
    try:
        # Delegate to stats service
        return stats_service.get_stats()
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving statistics: {str(e)}"
        )
