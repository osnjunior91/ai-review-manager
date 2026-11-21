
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from bson import ObjectId
from typing import Literal

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
        self.collection.create_index(
            [("created_at", DESCENDING), ("_id", DESCENDING)],
            name="idx_created_id"
        )
        self.collection.create_index(
            [("tenant_id", ASCENDING), ("platform", ASCENDING),
             ("created_at", DESCENDING)],
            name="idx_tenant_platform_created"
        )
        self.collection.create_index(
            [("status", ASCENDING), ("processed_at", DESCENDING)],
            name="idx_status_processed"
        )
        self.collection.create_index(
            [("ai_provider", ASCENDING), ("ai_model", ASCENDING),
             ("processed_at", DESCENDING)],
            name="idx_usage"
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
        analysis: dict,
        ai_provider: str,
        ai_model: str,
        review_comment: str,
        input_tokens: int | None,
        output_tokens: int | None,
        total_tokens: int | None
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
                    "review_comment": review_comment,
                    "analysis": analysis,
                    "ai_provider": ai_provider,
                    "ai_model": ai_model,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": total_tokens,
                    "processed_at": now,
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

 
    def fail(
        self,
        tenant_id: str,
        platform: str,
        external_review_id: str,
        processing_token: str,
        error_message: str
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
                    "status": "FAILED",
                    "last_error": error_message,
                    "updated_at": now
                },
                "$unset": {
                    "processing_token": "",
                    "lease_until": ""
                }
            }
        )

        return result.modified_count == 1

    def _date_filter(
        self,
        start_date: datetime | None,
        end_date: datetime | None,
        date_field: str = "processed_at"
    ) -> dict:
        if start_date is not None and start_date.tzinfo is None:
            start_date = start_date.replace(tzinfo=timezone.utc)
        if end_date is not None and end_date.tzinfo is None:
            end_date = end_date.replace(tzinfo=timezone.utc)
        if start_date is None and end_date is None:
            return {}

        value = {"$ifNull": [f"${date_field}", "$created_at"]}
        clauses = []
        if start_date is not None:
            clauses.append({"$gte": [value, start_date]})
        if end_date is not None:
            clauses.append({"$lt": [value, end_date]})

        return {"$expr": {"$and": clauses}} if len(clauses) > 1 else {"$expr": clauses[0]}

    def list_analyses(
        self,
        page: int,
        page_size: int,
        tenant_id: str | None = None,
        platform: str | None = None,
        status: str | None = None,
        sentiment: str | None = None,
        severity: str | None = None,
        requires_attention: bool | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None
    ) -> tuple[list[dict], int]:
        query: dict = {}
        if tenant_id:
            query["tenant_id"] = tenant_id
        if platform:
            query["platform"] = platform
        if status:
            query["status"] = status
        if sentiment:
            query["analysis.sentiment"] = sentiment
        if severity:
            query["analysis.severity"] = severity
        if requires_attention is not None:
            query["analysis.requires_attention"] = requires_attention
        query.update(self._date_filter(start_date, end_date))

        total = self.collection.count_documents(query)
        cursor = (
            self.collection.find(query)
            .sort([("created_at", DESCENDING), ("_id", DESCENDING)])
            .skip((page - 1) * page_size)
            .limit(page_size)
        )
        return list(cursor), total

    def find_by_id(
        self,
        analysis_id: str,
        tenant_id: str | None = None
    ) -> dict | None:
        query: dict = {"_id": ObjectId(analysis_id)}
        if tenant_id:
            query["tenant_id"] = tenant_id
        return self.collection.find_one(query)

    def get_statistics(
        self,
        tenant_id: str | None = None,
        platform: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None
    ) -> dict:
        match: dict = {}
        if tenant_id:
            match["tenant_id"] = tenant_id
        if platform:
            match["platform"] = platform
        match.update(self._date_filter(start_date, end_date))

        pipeline = []
        if match:
            pipeline.append({"$match": match})
        pipeline.append({
            "$facet": {
                "totals": [
                    {"$group": {
                        "_id": None,
                        "total": {"$sum": 1},
                        "completed": {"$sum": {"$cond": [{"$eq": ["$status", "COMPLETED"]}, 1, 0]}},
                        "processing": {"$sum": {"$cond": [{"$eq": ["$status", "PROCESSING"]}, 1, 0]}},
                        "failed": {"$sum": {"$cond": [{"$eq": ["$status", "FAILED"]}, 1, 0]}},
                    }},
                ],
                "valid": [
                    {"$match": {
                        "status": "COMPLETED",
                        "analysis": {"$ne": None},
                    }},
                    {"$facet": {
                        "sentiments": [
                            {"$match": {"analysis.sentiment": {"$in": ["POSITIVE", "NEGATIVE", "NEUTRAL", "MIXED"]}}},
                            {"$group": {"_id": "$analysis.sentiment", "count": {"$sum": 1}}},
                        ],
                        "severities": [
                            {"$match": {"analysis.severity": {"$in": ["LOW", "MEDIUM", "HIGH"]}}},
                            {"$group": {"_id": "$analysis.severity", "count": {"$sum": 1}}},
                        ],
                        "metrics": [
                            {"$group": {
                                "_id": None,
                                "average": {"$avg": "$analysis.satisfaction_score"},
                                "requires_attention": {"$sum": {"$cond": [{"$eq": ["$analysis.requires_attention", True]}, 1, 0]}},
                                "valid_count": {"$sum": 1},
                                "negative": {"$sum": {"$cond": [{"$eq": ["$analysis.sentiment", "NEGATIVE"]}, 1, 0]}},
                            }},
                        ],
                        "keywords": [
                            {"$unwind": "$analysis.keywords"},
                            {"$match": {"analysis.keywords": {"$ne": None}}},
                            {"$group": {"_id": {"$toLower": "$analysis.keywords"}, "count": {"$sum": 1}}},
                            {"$sort": {"count": -1, "_id": 1}},
                            {"$limit": 10},
                        ],
                        "criticisms": [
                            {"$unwind": "$analysis.criticisms"},
                            {"$match": {"analysis.criticisms": {"$ne": None}}},
                            {"$group": {"_id": {"$toLower": "$analysis.criticisms"}, "count": {"$sum": 1}}},
                            {"$sort": {"count": -1, "_id": 1}},
                            {"$limit": 10},
                        ],
                        "categories": [
                            {"$unwind": "$analysis.categories"},
                            {"$match": {"analysis.categories": {"$in": ["PRODUCT", "DELIVERY", "SERVICE", "PRICE", "OTHER"]}}},
                            {"$group": {"_id": "$analysis.categories", "count": {"$sum": 1}}},
                        ],
                    }},
                ],
            }
        })

        result = list(self.collection.aggregate(pipeline))
        return result[0] if result else {"totals": [], "valid": []}

    def get_usage(
        self,
        tenant_id: str | None = None,
        ai_provider: str | None = None,
        ai_model: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        group_by: Literal["day", "month", "model", "provider"] = "model"
    ) -> dict:
        match: dict = {}
        if tenant_id:
            match["tenant_id"] = tenant_id
        if ai_provider:
            match["ai_provider"] = ai_provider
        if ai_model:
            match["ai_model"] = ai_model
        match.update(self._date_filter(start_date, end_date))

        if group_by == "day":
            group_id = {"$dateToString": {"format": "%Y-%m-%d", "date": {"$ifNull": ["$processed_at", "$created_at"]}, "timezone": "UTC"}}
        elif group_by == "month":
            group_id = {"$dateToString": {"format": "%Y-%m", "date": {"$ifNull": ["$processed_at", "$created_at"]}, "timezone": "UTC"}}
        elif group_by == "provider":
            group_id = {"$ifNull": ["$ai_provider", "__unknown__"]}
        else:
            group_id = {"$ifNull": ["$ai_model", "__unknown__"]}

        pipeline = []
        if match:
            pipeline.append({"$match": match})
        pipeline.extend([
            {"$set": {
                "input_complete": {"$and": [{"$ne": ["$input_tokens", None]}, {"$gte": ["$input_tokens", 0]}]},
                "output_complete": {"$and": [{"$ne": ["$output_tokens", None]}, {"$gte": ["$output_tokens", 0]}]},
                "total_complete": {"$and": [{"$ne": ["$total_tokens", None]}, {"$gte": ["$total_tokens", 0]}]},
            }},
            {"$group": {
                "_id": group_id,
                "analyses": {"$sum": 1},
                "complete_metric_analyses": {"$sum": {"$cond": [
                    {"$and": ["$input_complete", "$output_complete", "$total_complete"]}, 1, 0
                ]}},
                "input_tokens": {"$sum": {"$ifNull": ["$input_tokens", 0]}},
                "output_tokens": {"$sum": {"$ifNull": ["$output_tokens", 0]}},
                "total_tokens": {"$sum": {"$ifNull": ["$total_tokens", 0]}},
                "input_known": {"$sum": {"$cond": ["$input_complete", "$input_tokens", 0]}},
                "output_known": {"$sum": {"$cond": ["$output_complete", "$output_tokens", 0]}},
                "total_known": {"$sum": {"$cond": ["$total_complete", "$total_tokens", 0]}},
                "input_nulls": {"$sum": {"$cond": ["$input_complete", 0, 1]}},
                "output_nulls": {"$sum": {"$cond": ["$output_complete", 0, 1]}},
                "total_nulls": {"$sum": {"$cond": ["$total_complete", 0, 1]}},
                "model": {"$first": "$ai_model"},
                "provider": {"$first": "$ai_provider"},
            }},
            {"$sort": {"_id": 1}},
        ])
        groups = list(self.collection.aggregate(pipeline))

        return {"groups": groups}



