from pydantic import BaseModel, ConfigDict


class RecommendationItem(BaseModel):
    """
    A single ranked project recommendation returned to the student.
    Includes the full score breakdown alongside the final match score.
    """
    project_id: int
    title: str
    match_score: float      # 0.0 – 100.0, final weighted score
    rank: int               # 1 = best match
    skill_score: float
    experience_score: float
    interest_score: float
    activity_score: float
    success_score: float

    model_config = ConfigDict(from_attributes=True)