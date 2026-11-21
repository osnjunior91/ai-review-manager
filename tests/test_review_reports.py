from datetime import datetime, timezone
from unittest.mock import Mock

from bson import ObjectId
from fastapi.testclient import TestClient

from app.main import app
from app.core.dependencies import get_review_batch_service
from app.services.review_query_service import ReviewQueryService
from app.services.review_statistics_service import ReviewStatisticsService


class RepositoryStub:
    pass


def test_invalid_object_id():
    service = ReviewQueryService(Mock())
    from fastapi import HTTPException

    try:
        service.get_analysis("invalid", None)
    except HTTPException as error:
        assert error.status_code == 400
    else:
        raise AssertionError("Expected HTTP 400")


def test_analysis_not_found():
    repository = Mock()
    repository.find_by_id.return_value = None
    service = ReviewQueryService(repository)
    from fastapi import HTTPException

    try:
        service.get_analysis(str(ObjectId()), "loja-001")
    except HTTPException as error:
        assert error.status_code == 404
    else:
        raise AssertionError("Expected HTTP 404")


def test_paginated_list_response():
    now = datetime.now(timezone.utc)
    oid = ObjectId()
    repository = Mock()
    repository.list_analyses.return_value = (
        [{"_id": oid, "tenant_id": "loja", "platform": "IFOOD",
          "external_review_id": "1", "status": "COMPLETED",
          "created_at": now, "updated_at": now,
          "processing_token": "secret"}],
        21,
    )
    service = ReviewQueryService(repository)
    result = service.list_analyses(
        2, 10, None, None, None, None, None, None, None, None
    )
    assert result["page"] == 2
    assert result["page_count"] == 3
    assert result["items"][0]["id"] == str(oid)
    assert "processing_token" not in result["items"][0]


def test_statistics_mixed_values():
    repository = Mock()
    repository.get_statistics.return_value = {
        "totals": [{"total": 4, "completed": 3, "processing": 1, "failed": 0}],
        "valid": [{
            "sentiments": [
                {"_id": "POSITIVE", "count": 1},
                {"_id": "NEGATIVE", "count": 1},
                {"_id": "MIXED", "count": 1},
            ],
            "severities": [{"_id": "HIGH", "count": 1}],
            "metrics": [{"average": 7.333, "requires_attention": 1,
                         "valid_count": 3, "negative": 1}],
            "keywords": [{"_id": "entrega", "count": 2}],
            "criticisms": [{"_id": "demora", "count": 2}],
            "categories": [{"_id": "DELIVERY", "count": 2}],
        }],
    }
    result = ReviewStatisticsService(repository).get_statistics(
        None, None, None, None
    )
    assert result["average_satisfaction"] == 7.33
    assert result["negative_percentage"] == 33.33
    assert result["sentiments"]["POSITIVE"] == 1
    assert result["top_keywords"][0]["keyword"] == "entrega"


def test_usage_missing_metrics():
    repository = Mock()
    repository.get_usage.return_value = {
        "groups": [{
            "_id": "__unknown__",
            "analyses": 2,
            "complete_metric_analyses": 1,
            "input_known": 100,
            "output_known": 25,
            "total_known": 125,
            "input_nulls": 1,
            "output_nulls": 1,
            "total_nulls": 1,
            "model": None,
        }]
    }
    result = ReviewStatisticsService(repository).get_usage(
        None, None, None, None, None, "model"
    )
    assert result["unknown_metric_analyses"] == 1
    assert result["estimated_cost_usd"] is None
    assert result["cost_is_complete"] is False


def test_swagger_exposes_report_routes():
    client = TestClient(app)
    schema = client.get("/openapi.json").json()
    assert "/reviews/analyses" in schema["paths"]
    assert "/reviews/analyses/{analysis_id}" in schema["paths"]
    assert "/reviews/statistics" in schema["paths"]
    assert "/reviews/usage" in schema["paths"]


def test_invalid_pagination_is_rejected():
    client = TestClient(app)
    response = client.get("/reviews/analyses?page=0")
    assert response.status_code == 422


def test_filter_period_is_passed_to_repository():
    repository = Mock()
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    end = datetime(2026, 2, 1, tzinfo=timezone.utc)
    repository.list_analyses.return_value = ([], 0)
    service = ReviewQueryService(repository)

    service.list_analyses(
        1, 20, "loja", "IFOOD", "COMPLETED", "POSITIVE",
        "LOW", True, start, end
    )

    repository.list_analyses.assert_called_once()
    kwargs = repository.list_analyses.call_args.kwargs
    assert kwargs["tenant_id"] == "loja"
    assert kwargs["sentiment"] == "POSITIVE"
    assert kwargs["start_date"] == start
    assert kwargs["end_date"] == end


def test_post_analyze_endpoint_regression():
    batch_service = Mock()
    batch_service.process_random.return_value = {
        "requested": 1,
        "available": 1,
        "selected": 1,
        "completed": 1,
        "processing": 0,
        "failed": 0,
        "items": [],
    }
    app.dependency_overrides[get_review_batch_service] = lambda: batch_service
    try:
        client = TestClient(app)
        response = client.post("/reviews/analyze", json={"quantity": 1})
        assert response.status_code == 200
        assert response.json()["completed"] == 1
        batch_service.process_random.assert_called_once_with(1)
    finally:
        app.dependency_overrides.clear()
