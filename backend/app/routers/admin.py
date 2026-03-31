from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Project, User
from app.schemas.project import ProjectRead
from app.core.dependencies import require_role

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/projects", response_model=list[ProjectRead])
def admin_get_all_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Returns all projects regardless of status.

    Admins can see all projects, including disabled ones, for oversight and management purposes.
    """
    return db.query(Project).order_by(Project.created_at.desc()).all()


@router.delete("/listings/{project_id}", status_code=status.HTTP_200_OK)
def disable_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Soft-deletes a project by setting its status to 'disabled'.
    
    This allows admins to remove inappropriate or outdated listings without permanently deleting data.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    project.status = "disabled"
    db.commit()
    return {"detail": f"Project {project_id} has been disabled"}


@router.put("/users/{user_id}/status", status_code=status.HTTP_200_OK)
def update_user_status(
    user_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Suspends or reactivates a user account.
    
    Admins can set is_active to False to suspend a user, preventing them from logging in or interacting with the system.
    Setting is_active to True reactivates the account.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_active = is_active
    db.commit()
    return {"detail": f"User {user_id} is_active set to {is_active}"}