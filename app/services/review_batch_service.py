
import json
import random
from pathlib import Path

from app.models.review import Review
from app.repositories.review_analysis_repository import (
    ReviewAnalysisRepository,
)
from app.services.review_processing_service import (
    ReviewProcessingService,
)


DATA_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "reviews_mock.json"
)


class ReviewBatchService:

    def __init__(
        self,
        repository: ReviewAnalysisRepository,
        processing_service: ReviewProcessingService
    ):
        self.repository = repository
        self.processing_service = processing_service

    def process_random(self, quantity: int) -> dict:

        # Load reviews from JSON
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        reviews = [
            Review.model_validate(item)
            for item in data["reviews"]
        ]

        tenant_id = "nuvem-roxa-001"
        platform = "IFOOD"

        # Select reviews not yet completed
        eligible = []

        for review in reviews:
            existing = self.repository.find(
                tenant_id=tenant_id,
                platform=platform,
                external_review_id=review.id
            )

            if existing is None or existing.status != "COMPLETED":
                eligible.append(review)

        # Select randomly, without repetition
        selected = random.sample(
            eligible,
            k=min(quantity, len(eligible))
        )

        results = {
            "requested": quantity,
            "available": len(eligible),
            "selected": len(selected),
            "completed": 0,
            "processing": 0,
            "failed": 0,
            "items": []
        }

        for review in selected:
            try:
                result = self.processing_service.process(
                    tenant_id=tenant_id,
                    platform=platform,
                    external_review_id=review.id,
                    review_comment=review.comment
                )

                if result.status == "COMPLETED":
                    results["completed"] += 1
                else:
                    results["processing"] += 1

                results["items"].append({
                    "review_id": review.id,
                    "status": result.status,
                    "from_cache": result.from_cache,
                    "sentiment": (
                        result.analysis.sentiment
                        if result.analysis else None
                    )
                })

            except Exception as error:
                results["failed"] += 1

                results["items"].append({
                    "review_id": review.id,
                    "status": "FAILED",
                    "error": type(error).__name__
                })

        return results
