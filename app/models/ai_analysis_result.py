
from typing import Literal
from pydantic import BaseModel, Field


class AIAnalysisResult(BaseModel):
    sentiment: Literal[
        "POSITIVE", "NEGATIVE", "NEUTRAL", "MIXED"
    ]

    satisfaction_score: int = Field(ge=1, le=10)
    score_reason: str = Field(min_length=10)

    keywords: list[str]
    praises: list[str]
    criticisms: list[str]

    categories: list[
        Literal[
            "PRODUCT",
            "DELIVERY",
            "SERVICE",
            "PRICE",
            "OTHER"
        ]
    ]

    severity: Literal["LOW", "MEDIUM", "HIGH"]
    requires_attention: bool

    suggested_reply: str = Field(min_length=1)
