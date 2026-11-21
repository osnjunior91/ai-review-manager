
from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.dependencies import get_review_batch_service
from app.models.analyze_reviews_request import (
    AnalyzeReviewsRequest,
)
from app.services.review_batch_service import (
    ReviewBatchService,
)


router = APIRouter(
    prefix="/reviews",
    tags=["Review Analysis"]
)


@router.post("/analyze")
def analyze_reviews(
    request: AnalyzeReviewsRequest,
    service: Annotated[
        ReviewBatchService,
        Depends(get_review_batch_service)
    ]
):
    return service.process_random(request.quantity)
