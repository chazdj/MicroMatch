from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import StudentProfile, User
from app.schemas.student_profile import StudentProfileCreate, StudentProfileRead, StudentProfileUpdate
from app.core.dependencies import require_role

router = APIRouter(prefix="/student/profile", tags=["Student Profile"])

@router.post("", response_model=StudentProfileRead, status_code=status.HTTP_201_CREATED)
def create_student_profile(
    profile_data: StudentProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    """
    Create a new student profile for the authenticated student.

    - Only users with role "student" can access this endpoint.
    - A student can only have one profile.
    """

    # Check if profile already exists for this user
    existing_profile = db.query(StudentProfile).filter_by(user_id=current_user.id).first()
    if existing_profile:
        raise HTTPException(status_code=400, detail="Profile already exists")

    # Create the profile
    profile = StudentProfile(user_id=current_user.id, **profile_data.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

@router.get("", response_model=StudentProfileRead)
def get_student_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    """
    Retrieve the authenticated student's profile.
    
    Returns 404 if no profile exists.
    """

    profile = db.query(StudentProfile).filter_by(user_id=current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.put("", response_model=StudentProfileRead)
def update_student_profile(
    profile_data: StudentProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    """
    Update the authenticated student's profile. 
    
    - Only provided fields will be updated.
    - Returns 404 if no profile exists.
    """
    profile = db.query(StudentProfile).filter_by(user_id=current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Update only provided fields
    for field, value in profile_data.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile

@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_student_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    """
    Delete the authenticated student's profile.

    Returns 404 if no profile exists.
    """
    profile = db.query(StudentProfile).filter_by(user_id=current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    db.delete(profile)
    db.commit()
