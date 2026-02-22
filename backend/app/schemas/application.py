from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ApplicationBase(BaseModel):
    """
    Shared attributes for Application models.
    """

    project_id: int

    model_config = ConfigDict(from_attributes=True)


class ApplicationCreate(ApplicationBase):
    """
    Schema used when a student applies to a project.
    """
    pass


class ApplicationRead(BaseModel):
    """
    Schema returned when retrieving an application.
    """

    id: int
    student_id: int
    project_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)