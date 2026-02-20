from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List
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

@router.get("", response_model=List[ProjectRead])
def get_projects(
    search: str | None = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Retrieve open projects.
    Supports optional keyword search and pagination.
    """

    query = db.query(Project).filter(Project.status == "open").order_by(Project.created_at.desc())
    
    # Keyword search (title OR description)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Project.title.ilike(search_term),
                Project.description.ilike(search_term)
            )
        )

    projects = query.offset(skip).limit(limit).all()

    return projects