
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

from app.models.ai_analysis_result import AIAnalysisResult


ProcessingStatus = Literal[
    "PROCESSING",
    "COMPLETED",
    "FAILED"
]

ReplyStatus = Literal[
    "PENDING_APPROVAL",
    "APPROVED",
    "REJECTED"
]


class ReviewAnalysis(BaseModel):
    # Review identity
    tenant_id: str = Field(min_length=1)
    platform: str = Field(min_length=1)
    external_review_id: str = Field(min_length=1)

    # Processing control
    status: ProcessingStatus = "PROCESSING"
    processing_token: str | None = None
    lease_until: datetime | None = None
    last_error: str | None = None

    # AI result
    analysis: AIAnalysisResult | None = None

    # AI metadata
    ai_provider: str | None = None
    ai_model: str | None = None

    input_tokens: int | None = Field(
        default=None,
        ge=0
    )
    output_tokens: int | None = Field(
        default=None,
        ge=0
    )
    total_tokens: int | None = Field(
        default=None,
        ge=0
    )

    # Reply approval
    reply_status: ReplyStatus = "PENDING_APPROVAL"

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    processed_at: datetime | None = None
