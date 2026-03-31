from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.schemas.student_profile import StudentProfileRead

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

class ApplicationStatusUpdate(BaseModel):
    """
    Schema used for updating the status of an application.

    Valid statuses:
    - accepted
    - rejected

    Validation of allowed transitions is handled in the router layer.
    """

    status: str

    model_config = ConfigDict(from_attributes=True)

class ProjectSummary(BaseModel):
    id: int
    title: str
    status: str
    model_config = ConfigDict(from_attributes=True)

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

    project: ProjectSummary | None = None

    model_config = ConfigDict(from_attributes=True)

class StudentApplicationInfo(BaseModel):
    """
    Safe student information exposed to organizations.
    """

    id: int
    email: str
    student_profile: StudentProfileRead | None = None

    model_config = ConfigDict(from_attributes=True)

class ApplicationWithStudentRead(BaseModel):
    """
    Schema returned when an organization views applications
    submitted to one of their projects.

    Includes:
    - Application metadata
    - Nested student information
    """

    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    student: StudentApplicationInfo

    model_config = ConfigDict(from_attributes=True)