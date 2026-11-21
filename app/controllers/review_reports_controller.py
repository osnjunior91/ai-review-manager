from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import (
    get_review_query_service,
    get_review_statistics_service,
)
from app.models.review_query_models import (
    AnalysisListResponse,
    AnalysisListItem,
    ReviewStatisticsResponse,
    ReviewUsageResponse,
)
from app.services.review_query_service import ReviewQueryService
from app.services.review_statistics_service import ReviewStatisticsService


router = APIRouter(prefix="/reviews", tags=["Review Reports"])


def validate_date_range(
    start_date: datetime | None,
    end_date: datetime | None,
) -> None:
    if start_date is not None and end_date is not None and start_date >= end_date:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=422,
            detail="start_date must be earlier than end_date",
        )


@router.get("/analyses", response_model=AnalysisListResponse)
def list_analyses(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    tenant_id: str | None = None,
    platform: str | None = None,
    status: Literal["PROCESSING", "COMPLETED", "FAILED"] | None = None,
    sentiment: Literal["POSITIVE", "NEGATIVE", "NEUTRAL", "MIXED"] | None = None,
    severity: Literal["LOW", "MEDIUM", "HIGH"] | None = None,
    requires_attention: bool | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    service: Annotated[ReviewQueryService, Depends(get_review_query_service)] = None,
):
    validate_date_range(start_date, end_date)
    return service.list_analyses(
        page, page_size, tenant_id, platform, status, sentiment,
        severity, requires_attention, start_date, end_date,
    )


@router.get("/analyses/{analysis_id}", response_model=AnalysisListItem)
def get_analysis(
    analysis_id: str,
    tenant_id: str | None = None,
    service: Annotated[ReviewQueryService, Depends(get_review_query_service)] = None,
):
    return service.get_analysis(analysis_id, tenant_id)


@router.get("/statistics", response_model=ReviewStatisticsResponse)
def get_statistics(
    tenant_id: str | None = None,
    platform: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    service: Annotated[ReviewStatisticsService, Depends(get_review_statistics_service)] = None,
):
    validate_date_range(start_date, end_date)
    return service.get_statistics(
        tenant_id, platform, start_date, end_date
    )


@router.get("/usage", response_model=ReviewUsageResponse)
def get_usage(
    tenant_id: str | None = None,
    ai_provider: str | None = None,
    ai_model: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    group_by: Literal["day", "month", "model", "provider"] = "model",
    service: Annotated[ReviewStatisticsService, Depends(get_review_statistics_service)] = None,
):
    validate_date_range(start_date, end_date)
    return service.get_usage(
        tenant_id, ai_provider, ai_model, start_date, end_date, group_by
    )
