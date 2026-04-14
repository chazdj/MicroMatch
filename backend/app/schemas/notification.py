from pydantic import BaseModel, ConfigDict
from datetime import datetime


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    recipient_id: int
    message: str
    is_read: bool
    created_at: datetime