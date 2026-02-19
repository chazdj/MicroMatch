from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Project, User
from app.schemas.project import ProjectCreate, ProjectRead
from app.core.dependencies import require_role

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("organization"))
):
    """
    Creates a new project owned by the authenticated organization.
    """
    
    project = Project(
        organization_id=current_user.id,
        **project_data.model_dump()
    )

    db.add(project)
    db.commit()
    db.refresh(project)
    return project
