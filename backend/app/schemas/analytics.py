from pydantic import BaseModel, ConfigDict


class StudentAnalytics(BaseModel):
    """Metrics for an authenticated student."""
    applications_submitted: int
    accepted_applications: int
    completed_projects: int
    average_feedback_rating: float | None  # None if no feedback exists yet

    model_config = ConfigDict(from_attributes=True)


class OrganizationAnalytics(BaseModel):
    """Metrics for an authenticated organization."""
    total_projects_posted: int
    active_projects: int
    completed_projects: int
    total_applicants: int

    model_config = ConfigDict(from_attributes=True)