from datetime import datetime
from pydantic import BaseModel, Field

from app.models.review_reply import ReviewReply
from app.models.review_order import ReviewOrder

class Review(BaseModel):
    id: str
    score: int = Field(ge=1, le=5)
    previousScore: int
    hasScoreChanged: bool
    status: str
    comment: str
    replies: list[ReviewReply]
    createdAt: datetime
    order: ReviewOrder
    surveyId: str
    version: str
    visibility: str