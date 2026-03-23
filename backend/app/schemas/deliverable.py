from pydantic import BaseModel, ConfigDict
from datetime import datetime

class DeliverableCreate(BaseModel):
    content: str

class DeliverableReview(BaseModel):
    status: str  # "accepted" or "rejected"
    feedback: str | None = None

class DeliverableRead(BaseModel):
    id: int
    application_id: int
    content: str
    status: str
    feedback: str | None
    created_at: datetime
    reviewed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)