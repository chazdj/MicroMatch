from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
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
    Supports keyword search across title, description,
    and required_skills with pagination.
    """

    query = db.query(Project).filter(Project.status == "open").order_by(Project.created_at.desc())
    
    # Enhanced search
    if search:
        keywords = search.strip().split()

        search_filters = []

        for keyword in keywords:
            term = f"%{keyword}%"
            search_filters.append(
                or_(
                    Project.title.ilike(term),
                    Project.description.ilike(term),
                    Project.required_skills.ilike(term)
                )
            )

        # Match ALL keywords (AND logic)
        query = query.filter(and_(*search_filters))

    query = query.order_by(Project.created_at.desc())

    projects = query.offset(skip).limit(limit).all()

    return projects