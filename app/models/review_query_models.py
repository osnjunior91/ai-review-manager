from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class AnalysisListItem(BaseModel):
    id: str
    tenant_id: str
    platform: str
    external_review_id: str
    review_comment: str | None = None
    status: Literal["PROCESSING", "COMPLETED", "FAILED"]
    analysis: dict | None = None
    ai_provider: str | None = None
    ai_model: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    reply_status: str = "PENDING_APPROVAL"
    created_at: datetime
    updated_at: datetime
    processed_at: datetime | None = None
    last_error: str | None = None


class AnalysisListResponse(BaseModel):
    page: int
    page_size: int
    total: int
    page_count: int
    items: list[AnalysisListItem]


class CountItem(BaseModel):
    name: str
    count: int


class KeywordItem(BaseModel):
    keyword: str
    count: int


class ReviewStatisticsResponse(BaseModel):
    total_reviews: int
    completed: int
    processing: int
    failed: int
    average_satisfaction: float | None
    sentiments: dict[str, int]
    severities: dict[str, int]
    requires_attention: int
    negative_percentage: float
    top_keywords: list[KeywordItem]
    top_criticisms: list[KeywordItem]
    categories: dict[str, int]
    denominator_notes: dict[str, str]


class UsageGroup(BaseModel):
    key: str
    analyses: int
    complete_metric_analyses: int
    unknown_metric_analyses: int
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    estimated_cost_usd: float | None = None


class ReviewUsageResponse(BaseModel):
    total_analyses: int
    complete_metric_analyses: int
    unknown_metric_analyses: int
    input_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None
    average_tokens_per_analysis: float | None
    estimated_cost_usd: float | None
    average_estimated_cost_usd: float | None
    cost_is_complete: bool
    group_by: Literal["day", "month", "model", "provider"]
    groups: list[UsageGroup]
    limitations: list[str]
