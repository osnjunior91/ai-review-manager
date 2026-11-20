from datetime import datetime
from pydantic import BaseModel, Field

class ReviewReply(BaseModel):
    createdAt: datetime
    text: str
    from_: str = Field(alias="from")