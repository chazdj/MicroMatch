from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime


class FeedbackCreate(BaseModel):
    project_id: int
    rating: int
    comment: str | None = None

    @field_validator("rating")
    @classmethod
    def rating_must_be_valid(cls, v):
        if not 1 <= v <= 5:
            raise ValueError("Rating must be between 1 and 5")
        return v


class FeedbackRead(BaseModel):
    id: int
    user_id: int
    project_id: int
    rating: int
    comment: str | None = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)