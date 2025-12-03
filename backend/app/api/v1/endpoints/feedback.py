from fastapi import APIRouter
from app.schemas.feedback import FeedbackRequest, FeedbackResponse

router = APIRouter()

@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(feedback: FeedbackRequest):
    # TODO: Store feedback in PostgreSQL for retraining
    # TODO: Invalidate cache if necessary
    
    print(f"Received feedback for {feedback.url}: is_phishing={feedback.is_phishing}")
    
    return FeedbackResponse(
        status="success",
        message="Feedback received successfully"
    )
