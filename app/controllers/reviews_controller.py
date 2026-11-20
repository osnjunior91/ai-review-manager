import json
from pathlib import Path

from fastapi import APIRouter

from app.models.reviews_response import ReviewsResponse

router = APIRouter(prefix="/reviews", tags=["Reviews"])

DATA_FILE = DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "reviews_mock.json"


@router.get("/", response_model=ReviewsResponse)
def read_reviews():
    if not DATA_FILE.is_file():
        raise FileNotFoundError(f"Reviews file not found: {DATA_FILE}")
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        DATA = json.load(f)
    return DATA
