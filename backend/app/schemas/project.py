from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ProjectBase(BaseModel):
    """
    Shared attributes for Project creation and reading.
    """

    title: str
    description: str
    required_skills: str | None = None
    duration: str | None = None

    model_config = ConfigDict(from_attributes=True)

class ProjectCreate(ProjectBase):
    """
    Schema for creating a new project.
    """
    pass

class ProjectRead(ProjectBase):
    """
    Schema returned when retrieving a project.
    """
    
    id: int
    organization_id: int
    status: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)