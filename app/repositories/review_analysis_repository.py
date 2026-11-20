
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from app.core.database import MongoDatabase
from app.models.review_analysis import ReviewAnalysis


class ReviewAnalysisRepository:

    def __init__(self, database: MongoDatabase):
        self.collection = database.get_collection(
            "review_analyses"
        )
        # Create a unique compound index
        self.collection.create_index(
            [
                ("tenant_id", ASCENDING),
                ("platform", ASCENDING),
                ("external_review_id", ASCENDING)
            ],
            unique=True,
            name="uq_tenant_platform_review"
        )

    def save(self, review: ReviewAnalysis) -> str:
        document = review.model_dump()

        result = self.collection.insert_one(document)

        return str(result.inserted_id)

    def find(
        self,
        tenant_id: str,
        platform: str,
        external_review_id: str
    ) -> ReviewAnalysis | None:

        document = self.collection.find_one({
            "tenant_id": tenant_id,
            "platform": platform,
            "external_review_id": external_review_id
        })

        if document is None:
            return None

        return ReviewAnalysis.model_validate(document)


    
    def try_acquire(
        self,
        tenant_id: str,
        platform: str,
        external_review_id: str,
        lease_seconds: int = 300
    ) -> str | None:

        now = datetime.now(timezone.utc)
        token = str(uuid4())
        lease_until = now + timedelta(seconds=lease_seconds)

        identity = {
            "tenant_id": tenant_id,
            "platform": platform,
            "external_review_id": external_review_id
        }

        try:
            self.collection.insert_one({
                **identity,
                "status": "PROCESSING",
                "processing_token": token,
                "lease_until": lease_until,
                "created_at": now,
                "updated_at": now
            })

            return token

        except DuplicateKeyError:
            pass

        document = self.collection.find_one_and_update(
            {
                **identity,
                "$or": [
                    {"status": "FAILED"},
                    {
                        "status": "PROCESSING",
                        "lease_until": {"$lte": now}
                    }
                ]
            },
            {
                "$set": {
                    "status": "PROCESSING",
                    "processing_token": token,
                    "lease_until": lease_until,
                    "updated_at": now,
                    "last_error": None
                }
            }
        )

        return token if document is not None else None

    
    def complete(
        self,
        tenant_id: str,
        platform: str,
        external_review_id: str,
        processing_token: str,
        analysis: dict
    ) -> bool:

        now = datetime.now(timezone.utc)

        result = self.collection.update_one(
            {
                "tenant_id": tenant_id,
                "platform": platform,
                "external_review_id": external_review_id,
                "status": "PROCESSING",
                "processing_token": processing_token,
                "lease_until": {"$gt": now}
            },
            {
                "$set": {
                    "status": "COMPLETED",
                    "analysis": analysis,
                    "completed_at": now,
                    "updated_at": now
                },
                "$unset": {
                    "processing_token": "",
                    "lease_until": "",
                    "last_error": ""
                }
            }
        )

        return result.modified_count == 1


