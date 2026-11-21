
from uuid import uuid4

from app.core.database import MongoDatabase
from app.repositories.review_analysis_repository import (
    ReviewAnalysisRepository,
)
from app.services.ai_analysis_service import AIAnalysisService
from app.services.review_processing_service import (
    ReviewProcessingService,
)


database = MongoDatabase()

try:
    repository = ReviewAnalysisRepository(database)
    ai_service = AIAnalysisService()

    service = ReviewProcessingService(
        repository=repository,
        ai_service=ai_service
    )

    # Unique ID to guarantee a new review
    review_id = str(uuid4())

    print("\n=== FIRST REQUEST ===")

    first = service.process(
        tenant_id="loja-001",
        platform="IFOOD",
        external_review_id=review_id,
        review_comment="Açaí maravilhoso, chegou rapidinho!"
    )

    print("Status:", first.status)
    print("From cache:", first.from_cache)
    print("Analysis:", first.analysis)

    print("\n=== SECOND REQUEST ===")

    second = service.process(
        tenant_id="loja-001",
        platform="IFOOD",
        external_review_id=review_id,
        review_comment="Açaí maravilhoso, chegou rapidinho!"
    )

    print("Status:", second.status)
    print("From cache:", second.from_cache)
    print("Analysis:", second.analysis)

    assert first.status == "COMPLETED"
    assert first.from_cache is False

    assert second.status == "COMPLETED"
    assert second.from_cache is True

    assert first.analysis == second.analysis

    print("\nALL TESTS PASSED!")

finally:
    database.close()
