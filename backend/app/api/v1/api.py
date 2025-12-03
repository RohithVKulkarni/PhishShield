from fastapi import APIRouter
from app.api.v1.endpoints import score, feedback, stats

api_router = APIRouter()
api_router.include_router(score.router, tags=["score"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
api_router.include_router(stats.router, tags=["stats"])
