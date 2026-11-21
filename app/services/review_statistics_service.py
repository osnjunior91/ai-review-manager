from datetime import datetime
from typing import Literal

from app.core.model_rates import MODEL_RATES_USD_PER_MILLION
from app.repositories.review_analysis_repository import ReviewAnalysisRepository


class ReviewStatisticsService:
    def __init__(self, repository: ReviewAnalysisRepository):
        self.repository = repository

    def get_statistics(
        self,
        tenant_id: str | None,
        platform: str | None,
        start_date: datetime | None,
        end_date: datetime | None,
    ) -> dict:
        raw = self.repository.get_statistics(
            tenant_id, platform, start_date, end_date
        )
        totals = raw.get("totals", [{}])[0] if raw.get("totals") else {}
        sentiments_rows = raw.get("sentiments", [])
        severities_rows = raw.get("severities", [])
        categories_rows = raw.get("categories", [])
        metrics_rows = raw.get("metrics", [])

        sentiments = {name: 0 for name in ["POSITIVE", "NEGATIVE", "NEUTRAL", "MIXED"]}
        severities = {name: 0 for name in ["LOW", "MEDIUM", "HIGH"]}
        categories = {name: 0 for name in ["PRODUCT", "DELIVERY", "SERVICE", "PRICE", "OTHER"]}
        for row in sentiments_rows:
            sentiments[row["_id"]] = row["count"]
        for row in severities_rows:
            severities[row["_id"]] = row["count"]
        for row in categories_rows:
            categories[row["_id"]] = row["count"]

        metrics = metrics_rows[0] if metrics_rows else {}
        negative = metrics.get("negative", 0)
        valid_count = metrics.get("valid_count", 0)
        negative_percentage = round(negative / valid_count * 100, 2) if valid_count else 0.0

        return {
            "total_reviews": totals.get("total", 0),
            "completed": totals.get("completed", 0),
            "processing": totals.get("processing", 0),
            "failed": totals.get("failed", 0),
            "average_satisfaction": (
                round(metrics["average"], 2) if metrics.get("average") is not None else None
            ),
            "sentiments": sentiments,
            "severities": severities,
            "requires_attention": metrics.get("requires_attention", 0),
            "negative_percentage": negative_percentage,
            "top_keywords": [
                {"keyword": row["_id"], "count": row["count"]}
                for row in raw.get("keywords", [])
            ],
            "top_criticisms": [
                {"keyword": row["_id"], "count": row["count"]}
                for row in raw.get("criticisms", [])
            ],
            "categories": categories,
            "denominator_notes": {
                "negative_percentage": "NEGATIVE completed analyses divided by all completed analyses with a valid analysis.",
                "average_satisfaction": "Average of satisfaction_score (1-10) across completed analyses with a valid analysis.",
            },
        }

    def get_usage(
        self,
        tenant_id: str | None,
        ai_provider: str | None,
        ai_model: str | None,
        start_date: datetime | None,
        end_date: datetime | None,
        group_by: Literal["day", "month", "model", "provider"],
    ) -> dict:
        raw = self.repository.get_usage(
            tenant_id, ai_provider, ai_model, start_date, end_date, group_by
        )
        groups = []
        total_analyses = 0
        complete_analyses = 0
        input_total = 0
        output_total = 0
        total_tokens = 0
        cost_complete = True
        estimated_total_cost = 0.0
        cost_known_analyses = 0

        for row in raw["groups"]:
            analyses = row["analyses"]
            complete = row["complete_metric_analyses"]
            unknown = analyses - complete
            total_analyses += analyses
            complete_analyses += complete

            input_known = row["input_known"] if row["input_nulls"] == 0 else None
            output_known = row["output_known"] if row["output_nulls"] == 0 else None
            total_known = row["total_known"] if row["total_nulls"] == 0 else None

            input_value = input_known
            output_value = output_known
            total_value = total_known
            if complete == analyses:
                input_total += input_known or 0
                output_total += output_known or 0
                total_tokens += total_known or 0

            model = str(row["_id"]) if group_by == "model" else None
            tariff = (
                MODEL_RATES_USD_PER_MILLION.get(model)
                if model is not None
                else None
            )
            cost = None
            if complete and tariff:
                input_complete_count = row["input_known"]
                output_complete_count = row["output_known"]
                cost = (
                    input_complete_count / 1_000_000 * tariff["input"]
                    + output_complete_count / 1_000_000 * tariff["output"]
                )
                estimated_total_cost += cost
                cost_known_analyses += complete
            elif unknown:
                cost_complete = False
            elif tariff is None:
                cost_complete = False

            groups.append({
                "key": str(row["_id"]),
                "analyses": analyses,
                "complete_metric_analyses": complete,
                "unknown_metric_analyses": unknown,
                "input_tokens": input_value,
                "output_tokens": output_value,
                "total_tokens": total_value,
                "estimated_cost_usd": round(cost, 8) if cost is not None else None,
            })

        if cost_known_analyses == 0:
            estimated_cost = None
        else:
            estimated_cost = round(estimated_total_cost, 8)

        has_unknown_totals = any(g["unknown_metric_analyses"] > 0 for g in groups)
        average = (
            round(total_tokens / complete_analyses, 2)
            if complete_analyses and not has_unknown_totals
            else None
        )

        return {
            "total_analyses": total_analyses,
            "complete_metric_analyses": complete_analyses,
            "unknown_metric_analyses": total_analyses - complete_analyses,
            "input_tokens": input_total if not has_unknown_totals else None,
            "output_tokens": output_total if not has_unknown_totals else None,
            "total_tokens": total_tokens if not has_unknown_totals else None,
            "average_tokens_per_analysis": average,
            "estimated_cost_usd": estimated_cost,
            "average_estimated_cost_usd": (
                round(estimated_cost / cost_known_analyses, 8)
                if estimated_cost is not None and cost_known_analyses
                else None
            ),
            "cost_is_complete": cost_complete and not has_unknown_totals,
            "group_by": group_by,
            "groups": groups,
            "limitations": [
                "Costs are estimates, not provider billing invoices.",
                "Recorded usage only; token consumption from failed persistence attempts may be absent.",
                "Unknown token metrics are not treated as zero.",
                "Unknown model tariffs are not assigned an invented cost.",
            ],
        }
