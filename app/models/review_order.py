from datetime import datetime
from pydantic import BaseModel

class ReviewOrder(BaseModel):
    id: str
    shortId: str
    createdAt: datetime