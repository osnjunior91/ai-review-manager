from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ReviewAnalysis(BaseModel):
    review_id: str

    sentiment: Literal[
        "POSITIVE",
        "NEGATIVE",
        "NEUTRAL",
        "MIXED"
    ]

    satisfaction_score: int = Field(ge=1, le=10)

    score_reason: str = Field(
        min_length=10,
        description="Explanation of the satisfaction score assigned by AI"
    )

    keywords: list[str]
    praises: list[str]
    criticisms: list[str]
    suggested_reply: str

    ai_provider: str
    ai_model: str
    processed_at: datetime

    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    total_tokens: int = Field(default=0, ge=0)