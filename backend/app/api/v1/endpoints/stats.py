from fastapi import APIRouter
from app.api.v1.endpoints.score import TOTAL_SCANS, THREATS_BLOCKED
import random

router = APIRouter()

@router.get("/stats")
async def get_stats():
    # Import here to get the latest values if they are updated in the other module
    from app.api.v1.endpoints.score import TOTAL_SCANS, THREATS_BLOCKED
    
    return {
        "total_scans": TOTAL_SCANS,
        "threats_neutralized": THREATS_BLOCKED,
        "active_nodes": 49, # Mock for now
        "latency": random.randint(20, 45) # Mock latency
    }
