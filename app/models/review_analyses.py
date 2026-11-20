from datetime import datetime
from pydantic import BaseModel

class ReviewAnalysis(BaseModel):
    review_id: str
    sentiment: str
    keywords: list[str]
    praises: list[str]
    criticisms: list[str]
    suggested_reply: str
    processed_at: datetime