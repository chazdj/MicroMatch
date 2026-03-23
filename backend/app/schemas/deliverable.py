from pydantic import BaseModel, ConfigDict
from datetime import datetime

class DeliverableCreate(BaseModel):
    content: str

class DeliverableRead(BaseModel):
    id: int
    application_id: int
    content: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)