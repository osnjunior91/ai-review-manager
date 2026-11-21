from pydantic import BaseModel, Field


class AnalyzeReviewsRequest(BaseModel):
    quantity: int = Field(ge=1, le=100)