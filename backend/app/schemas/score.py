from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class ScoreRequest(BaseModel):
    url: str

class ScoreResponse(BaseModel):
    url: str
    phishing_probability: float
    is_phishing: bool
    reasons: List[str] = []
    request_id: str
