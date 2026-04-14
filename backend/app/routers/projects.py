from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from sqlalchemy.sql import func

from typing import List
from app.database import get_db
from app.models import Project, User, Application, StudentProfile, Deliverable
from app.schemas.project import ProjectCreate, ProjectRead
from app.schemas.application import ApplicationWithStudentRead
from app.core.dependencies import require_role
from app.utils.notifications import create_notification

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

    query = db.query(Project).filter(Project.status.notin_(["disabled"])).filter(Project.status == "open").order_by(Project.created_at.desc())
    
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

@router.get("/me", response_model=List[ProjectRead])
def get_my_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("organization"))
):
    projects = (
        db.query(Project)
        .filter(Project.organization_id == current_user.id)
        .order_by(Project.created_at.desc())
        .all()
    )

    return projects

@router.get("/{project_id}/applications", response_model=List[ApplicationWithStudentRead], status_code=status.HTTP_200_OK)
def get_project_applications(
    project_id: int,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("organization"))
):
    """
    Allows an organization to view all student applications
    submitted to a specific project they own.

    Business Rules:
    - Only users with role "organization" may access this endpoint.
    - Project must exist.
    - Organization must own the project.
    - Results are paginated using skip and limit.
    - Returns application metadata and safe student information.

    Raises:
    - 404 if project not found
    - 403 if organization does not own project
    """

    # ---------------------------------------------------------
    # Validate project exists
    # ---------------------------------------------------------
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # ---------------------------------------------------------
    # Validate ownership
    # ---------------------------------------------------------
    if project.organization_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view these applications"
        )

    # ---------------------------------------------------------
    # Query applications with student + profile join
    # ---------------------------------------------------------
    applications = (
        db.query(Application)
        .filter(Application.project_id == project_id)
        .order_by(Application.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return applications

@router.put("/{project_id}/complete", response_model=ProjectRead)
def complete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("organization"))
):
    """
    Marks a project as completed by setting its status to "completed"
    and recording the completion timestamp.

    Business Rules:
    - Only users with role "organization" may access this endpoint.
    - Project must exist.
    - Organization must own the project.
    - Project must not already be completed.

    Raises:
    - 404 if project not found
    - 403 if organization does not own project
    - 400 if project is already completed
    """

    # ---------------------------------------------------------
    # Validate project exists
    # ---------------------------------------------------------
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # ---------------------------------------------------------
    # Validate ownership
    # ---------------------------------------------------------
    if project.organization_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to complete this project"
        )

    # Guard: must have an accepted deliverable (TC-US12-02)
    accepted = (
        db.query(Deliverable)
        .join(Application)
        .filter(
            Application.project_id == project_id,
            Deliverable.status == "accepted"
        )
        .first()
    )
    if not accepted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project cannot be completed until a deliverable has been accepted"
        )
    # ---------------------------------------------------------
    # Mark as completed
    # ---------------------------------------------------------
    project.status = "completed"
    project.completed_at = func.now()

    # ---------------------------------------------------------
    # Notify all accepted students of project completion
    # ---------------------------------------------------------
    accepted_applications = db.query(Application).filter(
        Application.project_id == project_id,
        Application.status == "accepted"
    ).all()

    for app in accepted_applications:
        create_notification(
            db,
            recipient_id=app.student_id,
            message=f"The project '{project.title}' has been marked complete. Congratulations!"
        )

    db.commit()
    db.refresh(project)

    return project