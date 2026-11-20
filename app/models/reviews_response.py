from pydantic import BaseModel
from app.models.review import Review

class ReviewsResponse(BaseModel):
    page: int
    size: int
    reviews: list[Review]
    total: int
    pageCount: int