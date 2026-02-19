from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import OrganizationProfile
from app.schemas.organization_profile import (
    OrganizationProfileCreate,
    OrganizationProfileResponse,
    OrganizationProfileUpdate,
)
from app.core.dependencies import require_role, get_current_user

router = APIRouter(prefix="/organization", tags=["organization"])

@router.post("/profile", response_model=OrganizationProfileResponse, status_code=201)
def create_organization_profile(
    profile_data: OrganizationProfileCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("organization"))
):
    """
    Creates an organization profile for the authenticated organization user.
    """

    # Check if profile already exists
    existing_profile = db.query(OrganizationProfile).filter_by(user_id=current_user.id).first()
    if existing_profile:
        raise HTTPException(status_code=409, detail="Profile already exists")

    # Create the profile
    new_profile = OrganizationProfile(
        user_id=current_user.id,
        **profile_data.model_dump()
    )
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return new_profile

@router.get("/profile", response_model=OrganizationProfileResponse)
def get_organization_profile(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("organization"))
):
    """
    Retrieves the authenticated organization's profile.
    """
    profile = db.query(OrganizationProfile).filter_by(user_id=current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.put("/profile", response_model=OrganizationProfileResponse)
def update_organization_profile(
    profile_update: OrganizationProfileUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("organization"))
):
    """
    Updates fields of the organization's profile.
    Only provided fields are updated.
    """

    profile = db.query(OrganizationProfile).filter_by(user_id=current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Apply partial updates
    for key, value in profile_update.model_dump(exclude_unset=True).items():
        setattr(profile, key, value)

    db.commit()
    db.refresh(profile)
    return profile

@router.delete("/profile", status_code=204)
def delete_organization_profile(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("organization"))
):
    """ 
    Deletes the organization's profile. 
    """
    profile = db.query(OrganizationProfile).filter_by(user_id=current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    db.delete(profile)
    db.commit()
    return