# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from app.database import get_db
# from app.models import StudentProfile, User
# from app.schemas.student_profile import (StudentProfileCreate, StudentProfileRead, StudentProfileUpdate)
# from app.core.dependencies import require_role, get_current_user

# router = APIRouter(prefix="/student", tags=["Student Profile"])

# @router.post("", response_model=StudentProfileRead, status_code=201) 
# def create_student_profile( 
#     profile_data: StudentProfileCreate, 
#     db: Session = Depends(get_db), 
#     current_user: User = Depends(require_role("student")) 
# ): 
#     existing = db.query(StudentProfile).filter_by(user_id=current_user.id).first() 
#     if existing: 
#         raise HTTPException(status_code=400, detail="Profile already exists") 
    
#     profile = StudentProfile(user_id=current_user.id, **profile_data.model_dump()) 
    
#     db.add(profile) 
#     db.commit() 
#     db.refresh(profile) 
#     return profile

# @router.get("", response_model=StudentProfileRead) 
# def get_student_profile( 
#     db: Session = Depends(get_db), 
#     current_user: User = Depends(require_role("student")) 
# ): 
#     profile = db.query(StudentProfile).filter_by(user_id=current_user.id).first() 
#     if not profile: 
#         raise HTTPException(status_code=404, detail="Profile not found") 
#     return profile 

# @router.put("", response_model=StudentProfileRead) 
# def update_student_profile( 
#     updated_data: StudentProfileUpdate, 
#     db: Session = Depends(get_db), 
#     current_user: User = Depends(require_role("student")) 
# ): 
#     profile = db.query(StudentProfile).filter_by(user_id=current_user.id).first() 
#     if not profile: 
#         raise HTTPException(status_code=404, detail="Profile not found") 
    
#     for field, value in updated_data.model_dump(exclude_unset=True).items(): 
#         setattr(profile, field, value) 
        
#     db.commit() 
#     db.refresh(profile) 
#     return profile 

# @router.delete("", status_code=204) 
# def delete_student_profile( 
#     db: Session = Depends(get_db), 
#     current_user: User = Depends(require_role("student")) 
# ): 
#     profile = db.query(StudentProfile).filter_by(user_id=current_user.id).first() 
#     if not profile: 
#         raise HTTPException(status_code=404, detail="Profile not found") 
    
#     db.delete(profile) 
#     db.commit()

# # # ------------------------
# # # Get own profile
# # # ------------------------
# # @router.get("/profile", response_model=StudentProfileRead)
# # def get_student_profile(
# #     current_user: dict = Depends(require_role("Student")),
# #     db: Session = Depends(get_db),
# # ):
# #     profile = db.query(StudentProfile).filter_by(user_id=current_user["user_id"]).first()
# #     if not profile:
# #         raise HTTPException(
# #             status_code=status.HTTP_404_NOT_FOUND,
# #             detail="Student profile not found"
# #         )
# #     return profile


# # # ------------------------
# # # Create profile
# # # ------------------------
# # @router.post("/profile", response_model=StudentProfileRead, status_code=201)
# # def create_student_profile(
# #     profile_data: StudentProfileCreate,
# #     current_user: dict = Depends(require_role("Student")),
# #     db: Session = Depends(get_db),
# # ):
# #     existing_profile = db.query(StudentProfile).filter_by(user_id=current_user["user_id"]).first()
# #     if existing_profile:
# #         raise HTTPException(
# #             status_code=status.HTTP_409_CONFLICT,
# #             detail="Profile already exists"
# #         )

# #     new_profile = StudentProfile(
# #         user_id=current_user["user_id"],
# #         **profile_data.dict()
# #     )

# #     db.add(new_profile)
# #     db.commit()
# #     db.refresh(new_profile)
# #     return new_profile


# # # ------------------------
# # # Update profile
# # # ------------------------
# # @router.put("/profile", response_model=StudentProfileRead)
# # def update_student_profile(
# #     profile_data: StudentProfileUpdate,
# #     current_user: dict = Depends(require_role("Student")),
# #     db: Session = Depends(get_db),
# # ):
# #     profile = db.query(StudentProfile).filter_by(user_id=current_user["user_id"]).first()
# #     if not profile:
# #         raise HTTPException(
# #             status_code=status.HTTP_404_NOT_FOUND,
# #             detail="Profile not found"
# #         )

# #     for key, value in profile_data.dict(exclude_unset=True).items():
# #         setattr(profile, key, value)

# #     db.commit()
# #     db.refresh(profile)
# #     return profile


# # # ------------------------
# # # Delete profile
# # # ------------------------
# # @router.delete("/profile", status_code=204)
# # def delete_student_profile(
# #     current_user: dict = Depends(require_role("Student")),
# #     db: Session = Depends(get_db),
# # ):
# #     profile = db.query(StudentProfile).filter_by(user_id=current_user["user_id"]).first()
# #     if not profile:
# #         raise HTTPException(
# #             status_code=status.HTTP_404_NOT_FOUND,
# #             detail="Profile not found"
# #         )

# #     db.delete(profile)
# #     db.commit()
# #     return {"detail": "Profile deleted successfully"}

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import StudentProfile, User
from app.schemas.student_profile import StudentProfileCreate, StudentProfileRead, StudentProfileUpdate
from app.core.dependencies import require_role

router = APIRouter(prefix="/student/profile", tags=["Student Profile"])

# ---------------------
# CREATE
# ---------------------
@router.post("", response_model=StudentProfileRead, status_code=status.HTTP_201_CREATED)
def create_student_profile(
    profile_data: StudentProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    existing_profile = db.query(StudentProfile).filter_by(user_id=current_user.id).first()
    if existing_profile:
        raise HTTPException(status_code=400, detail="Profile already exists")

    profile = StudentProfile(user_id=current_user.id, **profile_data.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

# ---------------------
# READ
# ---------------------
@router.get("", response_model=StudentProfileRead)
def get_student_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    profile = db.query(StudentProfile).filter_by(user_id=current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

# ---------------------
# UPDATE
# ---------------------
@router.put("", response_model=StudentProfileRead)
def update_student_profile(
    profile_data: StudentProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    profile = db.query(StudentProfile).filter_by(user_id=current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    for field, value in profile_data.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile

# ---------------------
# DELETE
# ---------------------
@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_student_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    profile = db.query(StudentProfile).filter_by(user_id=current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    db.delete(profile)
    db.commit()
