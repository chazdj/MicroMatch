from fastapi import APIRouter, Depends
from app.core.dependencies import require_role

router = APIRouter(tags=["student"])


@router.get("/student/profile")
def student_profile(current_user=Depends(require_role("Student"))):
    return {"message": "ok"}
