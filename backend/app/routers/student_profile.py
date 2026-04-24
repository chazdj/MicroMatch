# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from app.database import get_db
# from app.models import StudentProfile, User
# from app.schemas.student_profile import StudentProfileCreate, StudentProfileRead, StudentProfileUpdate
# from app.core.dependencies import require_role

# router = APIRouter(prefix="/student/profile", tags=["Student Profile"])

# def _build_profile_read(profile: StudentProfile, db: Session) -> StudentProfileRead:
#     """
#     Assembles a StudentProfileRead by augmenting the ORM object with
#     computed fields (completed_projects, average_rating) from the DB.
#     """
#     completed_projects = (
#         db.query(func.count(Application.id))
#         .join(Project, Project.id == Application.project_id)
#         .filter(
#             Application.student_id == profile.user_id,
#             Application.status == "accepted",
#             Project.status == "completed",
#         )
#         .scalar()
#     )

#     avg_rating_result = (
#         db.query(func.avg(Feedback.rating))
#         .filter(Feedback.user_id == profile.user_id)
#         .scalar()
#     )
#     average_rating = (
#         round(float(avg_rating_result), 2) if avg_rating_result is not None else None
#     )

#     return StudentProfileRead(
#         id=profile.id,
#         user_id=profile.user_id,
#         university=profile.university,
#         major=profile.major,
#         graduation_year=profile.graduation_year,
#         skills=profile.skills,
#         bio=profile.bio,
#         portfolio_links=profile.portfolio_links,
#         badges=profile.badges,
#         completed_projects=completed_projects,
#         average_rating=average_rating,
#     )

# @router.post("", response_model=StudentProfileRead, status_code=status.HTTP_201_CREATED)
# def create_student_profile(
#     profile_data: StudentProfileCreate,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(require_role("student")),
# ):
#     """
#     Create a new student profile for the authenticated student.

#     - Only users with role "student" can access this endpoint.
#     - A student can only have one profile.
#     """

#     # Check if profile already exists for this user
#     existing_profile = db.query(StudentProfile).filter_by(user_id=current_user.id).first()
#     if existing_profile:
#         raise HTTPException(status_code=400, detail="Profile already exists")

#     # Create the profile
#     profile = StudentProfile(user_id=current_user.id, **profile_data.model_dump())
#     db.add(profile)
#     db.commit()
#     db.refresh(profile)
#     return profile

# @router.get("", response_model=StudentProfileRead)
# def get_student_profile(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(require_role("student")),
# ):
#     """
#     Retrieve the authenticated student's profile.
    
#     Returns 404 if no profile exists.
#     """

#     profile = db.query(StudentProfile).filter_by(user_id=current_user.id).first()
#     if not profile:
#         raise HTTPException(status_code=404, detail="Profile not found")
#     return profile


# @router.put("", response_model=StudentProfileRead)
# def update_student_profile(
#     profile_data: StudentProfileUpdate,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(require_role("student")),
# ):
#     """
#     Update the authenticated student's profile. 
    
#     - Only provided fields will be updated.
#     - Returns 404 if no profile exists.
#     """
#     profile = db.query(StudentProfile).filter_by(user_id=current_user.id).first()
#     if not profile:
#         raise HTTPException(status_code=404, detail="Profile not found")

#     # Update only provided fields
#     for field, value in profile_data.model_dump(exclude_unset=True).items():
#         setattr(profile, field, value)

#     db.commit()
#     db.refresh(profile)
#     return profile

# @router.delete("", status_code=status.HTTP_204_NO_CONTENT)
# def delete_student_profile(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(require_role("student")),
# ):
#     """
#     Delete the authenticated student's profile.

#     Returns 404 if no profile exists.
#     """
#     profile = db.query(StudentProfile).filter_by(user_id=current_user.id).first()
#     if not profile:
#         raise HTTPException(status_code=404, detail="Profile not found")

#     db.delete(profile)
#     db.commit()

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import StudentProfile, User, Application, Project, Feedback
from app.schemas.student_profile import (
    StudentProfileCreate,
    StudentProfileRead,
    StudentProfileUpdate,
    StudentProfileEnhance,
)
from app.core.dependencies import require_role, get_current_user

router = APIRouter(prefix="/student/profile", tags=["Student Profile"])


def _build_profile_read(profile: StudentProfile, db: Session) -> StudentProfileRead:
    """
    Assembles a StudentProfileRead by augmenting the ORM object with
    computed fields (completed_projects, average_rating) from the DB.
    """
    completed_projects = (
        db.query(func.count(Application.id))
        .join(Project, Project.id == Application.project_id)
        .filter(
            Application.student_id == profile.user_id,
            Application.status == "accepted",
            Project.status == "completed",
        )
        .scalar()
    )

    avg_rating_result = (
        db.query(func.avg(Feedback.rating))
        .filter(Feedback.user_id == profile.user_id)
        .scalar()
    )
    average_rating = (
        round(float(avg_rating_result), 2) if avg_rating_result is not None else None
    )

    return StudentProfileRead(
        id=profile.id,
        user_id=profile.user_id,
        university=profile.university,
        major=profile.major,
        graduation_year=profile.graduation_year,
        skills=profile.skills,
        bio=profile.bio,
        portfolio_links=profile.portfolio_links,
        badges=profile.badges,
        completed_projects=completed_projects,
        average_rating=average_rating,
    )


@router.post("", response_model=StudentProfileRead, status_code=status.HTTP_201_CREATED)
def create_student_profile(
    profile_data: StudentProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    """
    Create a new student profile for the authenticated student.
    """
    existing_profile = db.query(StudentProfile).filter_by(user_id=current_user.id).first()
    if existing_profile:
        raise HTTPException(status_code=400, detail="Profile already exists")

    profile = StudentProfile(user_id=current_user.id, **profile_data.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return _build_profile_read(profile, db)


@router.get("", response_model=StudentProfileRead)
def get_my_student_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    """
    Retrieve the authenticated student's own profile with computed fields.
    """
    profile = db.query(StudentProfile).filter_by(user_id=current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return _build_profile_read(profile, db)


@router.get("/{student_id}", response_model=StudentProfileRead)
def get_student_profile_by_id(
    student_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    GET /profiles/student/{id}

    Retrieve any student's public profile by their user ID.
    Includes computed completed_projects and average_rating.
    Accessible to any authenticated user (orgs reviewing applicants, etc).

    Raises:
    - 404 if no profile exists for that student_id
    """
    profile = db.query(StudentProfile).filter_by(user_id=student_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return _build_profile_read(profile, db)


@router.put("", response_model=StudentProfileRead)
def update_student_profile(
    profile_data: StudentProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    """
    Update the authenticated student's core profile fields.
    Only provided fields are updated.
    """
    profile = db.query(StudentProfile).filter_by(user_id=current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    for field, value in profile_data.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return _build_profile_read(profile, db)


@router.put("/enhance", response_model=StudentProfileRead)
def enhance_student_profile(
    enhance_data: StudentProfileEnhance,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    """
    PUT /profiles/student/enhance

    Save enhancement fields to the student's profile:
    - portfolio_links (comma-separated URLs)
    - badges (comma-separated badge names, future-ready)

    Computed fields (completed_projects, average_rating) are derived
    live from the DB and returned in the response but never stored here.

    Raises:
    - 404 if no base profile exists yet
    """
    profile = db.query(StudentProfile).filter_by(user_id=current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found. Create a base profile before enhancing."
        )

    for field, value in enhance_data.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return _build_profile_read(profile, db)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_student_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    """
    Delete the authenticated student's profile.
    """
    profile = db.query(StudentProfile).filter_by(user_id=current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    db.delete(profile)
    db.commit()