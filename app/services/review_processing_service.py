
from dataclasses import dataclass
from typing import Literal

from app.core.config import get_settings
from app.models.ai_analysis_result import AIAnalysisResult
from app.repositories.review_analysis_repository import (
    ReviewAnalysisRepository,
)
from app.services.ai_analysis_service import AIAnalysisService


@dataclass
class ProcessingResult:
    status: Literal["COMPLETED", "PROCESSING"]
    analysis: AIAnalysisResult | None
    from_cache: bool


class ReviewProcessingService:

    def __init__(
        self,
        repository: ReviewAnalysisRepository,
        ai_service: AIAnalysisService
    ):
        self.repository = repository
        self.ai_service = ai_service

    def process(
        self,
        tenant_id: str,
        platform: str,
        external_review_id: str,
        review_comment: str
    ) -> ProcessingResult:

        # 1. Attempt to reserve processing
        token = self.repository.try_acquire(
            tenant_id=tenant_id,
            platform=platform,
            external_review_id=external_review_id
        )

        # 2. Reservation not acquired
        if token is None:
            existing = self.repository.find(
                tenant_id=tenant_id,
                platform=platform,
                external_review_id=external_review_id
            )

            if (
                existing is not None
                and existing.status == "COMPLETED"
                and existing.analysis is not None
            ):
                return ProcessingResult(
                    status="COMPLETED",
                    analysis=existing.analysis,
                    from_cache=True
                )

            return ProcessingResult(
                status="PROCESSING",
                analysis=None,
                from_cache=False
            )

        # 3. Reservation acquired: call AI
        try:
            response = self.ai_service.analyze(review_comment)

            # Validate AI response
            analysis = AIAnalysisResult.model_validate_json(
                response.content
            )

            # Dentro do método process()
            settings = get_settings()

            # 4. Persist result
            completed = self.repository.complete(
                tenant_id=tenant_id,
                platform=platform,
                external_review_id=external_review_id,
                processing_token=token,
                review_comment=review_comment,
                analysis=analysis.model_dump(),
                ai_provider=settings.ai_provider,
                ai_model=response.model,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                total_tokens=response.total_tokens
            )

            if not completed:
                raise RuntimeError(
                    "Could not complete processing: "
                    "reservation expired or was reassigned."
                )

            return ProcessingResult(
                status="COMPLETED",
                analysis=analysis,
                from_cache=False
            )

        except Exception as error:
            # 5. Register failure if this worker
            # still owns the reservation
            self.repository.fail(
                tenant_id=tenant_id,
                platform=platform,
                external_review_id=external_review_id,
                processing_token=token,
                error_message=str(error)
            )

            raise
