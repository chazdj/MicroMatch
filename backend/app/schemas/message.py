from pydantic import BaseModel, ConfigDict
from datetime import datetime


class MessageCreate(BaseModel):
    """Schema for sending a message in a project."""
    content: str

    model_config = ConfigDict(from_attributes=True)


class SenderInfo(BaseModel):
    """Safe sender info exposed in message responses."""
    id: int
    email: str
    role: str

    model_config = ConfigDict(from_attributes=True)


class MessageRead(BaseModel):
    """Schema returned when reading a project message."""
    id: int
    project_id: int
    sender_id: int
    content: str
    created_at: datetime
    sender: SenderInfo

    model_config = ConfigDict(from_attributes=True)