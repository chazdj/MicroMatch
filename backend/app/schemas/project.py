from pydantic import BaseModel, ConfigDict

class ProjectBase(BaseModel):
    title: str
    description: str
    required_skills: str | None = None
    duration: str | None = None

    model_config = ConfigDict(from_attributes=True)

class ProjectCreate(ProjectBase):
    pass

class ProjectRead(ProjectBase):
    id: int
    organization_id: int
    status: str
    created_at: str
