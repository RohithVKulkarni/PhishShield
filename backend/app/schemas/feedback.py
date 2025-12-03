from pydantic import BaseModel
from typing import Optional

class FeedbackRequest(BaseModel):
    url: str
    is_phishing: bool
    user_comment: Optional[str] = None
    request_id: Optional[str] = None

class FeedbackResponse(BaseModel):
    status: str
    message: str
