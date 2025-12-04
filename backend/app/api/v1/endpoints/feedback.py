"""
PhishShield AI - Feedback Endpoint

This module handles user feedback submission for improving the ML model.

Endpoints:
    POST /api/v1/feedback - Submit user feedback for a URL scan

Author: PhishShield Team
"""

from fastapi import APIRouter, HTTPException
from app.schemas.feedback import FeedbackRequest, FeedbackResponse
from app.services import feedback_service

router = APIRouter()


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(feedback: FeedbackRequest):
    """
    Submit user feedback for a URL scan.
    
    Allows users to correct false positives/negatives, helping improve
    the ML model through retraining.
    
    Args:
        feedback: FeedbackRequest containing:
            - url: The URL that was scanned
            - is_phishing: User's verdict (True = phishing, False = safe)
            - user_comment: Optional comment/explanation
            
    Returns:
        FeedbackResponse with status and message
        
    Example Request:
        POST /api/v1/feedback
        {
            "url": "http://example.com",
            "is_phishing": false,
            "user_comment": "This is a legitimate site"
        }
        
    Example Response:
        {
            "status": "success",
            "message": "Feedback received successfully"
        }
    """
    try:
        # Delegate to feedback service
        result = feedback_service.submit_feedback(
            url=feedback.url,
            is_phishing=feedback.is_phishing,
            user_comment=getattr(feedback, 'user_comment', None)
        )
        
        return FeedbackResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error submitting feedback: {str(e)}"
        )
