from math import ceil
from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException

from app.repositories.review_analysis_repository import ReviewAnalysisRepository


class ReviewQueryService:
    def __init__(self, repository: ReviewAnalysisRepository):
        self.repository = repository

    def list_analyses(
        self,
        page: int,
        page_size: int,
        tenant_id: str | None,
        platform: str | None,
        status: str | None,
        sentiment: str | None,
        severity: str | None,
        requires_attention: bool | None,
        start_date: datetime | None,
        end_date: datetime | None,
    ) -> dict:
        documents, total = self.repository.list_analyses(
            page=page,
            page_size=page_size,
            tenant_id=tenant_id,
            platform=platform,
            status=status,
            sentiment=sentiment,
            severity=severity,
            requires_attention=requires_attention,
            start_date=start_date,
            end_date=end_date,
        )
        items = []
        for document in documents:
            document = dict(document)
            document["id"] = str(document.pop("_id"))
            document.pop("processing_token", None)
            document.pop("lease_until", None)
            items.append(document)

        return {
            "page": page,
            "page_size": page_size,
            "total": total,
            "page_count": ceil(total / page_size) if total else 0,
            "items": items,
        }

    def get_analysis(self, analysis_id: str, tenant_id: str | None) -> dict:
        if not ObjectId.is_valid(analysis_id):
            raise HTTPException(status_code=400, detail="Invalid MongoDB ObjectId")

        document = self.repository.find_by_id(analysis_id, tenant_id)
        if document is None:
            raise HTTPException(status_code=404, detail="Analysis not found")

        document = dict(document)
        document["id"] = str(document.pop("_id"))
        document.pop("processing_token", None)
        document.pop("lease_until", None)
        return document
