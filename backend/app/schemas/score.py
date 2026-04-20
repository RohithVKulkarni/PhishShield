from pydantic import BaseModel
from typing import List, Optional


class ScoreRequest(BaseModel):
    url: str
    html_content: Optional[str] = None
    """
    Optional raw HTML of the page, pre-fetched by the browser extension.
    When provided, the HTML analyzer will parse it directly without making
    an additional HTTP request from the backend.
    """


class ScoreResponse(BaseModel):
    url: str
    phishing_probability: float
    is_phishing: bool
    reasons: List[str] = []
    request_id: str
    html_score: Optional[float] = None
    """HTML-only phishing score (0.0 safe – 1.0 suspicious). None if HTML was not analyzed."""
