
from typing import Generator

from fastapi import Depends

from app.core.database import MongoDatabase
from app.repositories.review_analysis_repository import (
    ReviewAnalysisRepository,
)
from app.services.ai_analysis_service import AIAnalysisService
from app.services.review_processing_service import (
    ReviewProcessingService,
)
from app.services.review_batch_service import (
    ReviewBatchService,
)


def get_review_processing_service() -> Generator[
    ReviewProcessingService, None, None
]:
    database = MongoDatabase()

    try:
        repository = ReviewAnalysisRepository(database)
        ai_service = AIAnalysisService()

        yield ReviewProcessingService(
            repository=repository,
            ai_service=ai_service
        )

    finally:
        database.close()


def get_review_batch_service(
    processing_service: ReviewProcessingService = Depends(
        get_review_processing_service
    )
) -> ReviewBatchService:

    return ReviewBatchService(
        repository=processing_service.repository,
        processing_service=processing_service
    )
