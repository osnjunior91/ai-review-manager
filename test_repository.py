
from uuid import uuid4

from app.core.database import MongoDatabase
from app.repositories.review_analysis_repository import (
    ReviewAnalysisRepository,
)

database = MongoDatabase()

try:
    repository = ReviewAnalysisRepository(database)
    review_id = str(uuid4())

    token = repository.try_acquire(
        tenant_id="loja-001",
        platform="IFOOD",
        external_review_id=review_id
    )

    print("Reserva:", token)

    completed = repository.complete(
        tenant_id="loja-001",
        platform="IFOOD",
        external_review_id=review_id,
        processing_token=token,
        analysis={
            "sentiment": "POSITIVE",
            "satisfaction_score": 10,
            "suggested_reply": "Muito obrigado pela avaliação!"
        }
    )

    print("Finalização:", completed)

    second_attempt = repository.try_acquire(
        tenant_id="loja-001",
        platform="IFOOD",
        external_review_id=review_id
    )

    print("Nova tentativa:", second_attempt)

finally:
    database.close()
