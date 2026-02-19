from pydantic import BaseModel, constr
from typing import Optional

class OrganizationProfileCreate(BaseModel):
    """
    Schema for creating a new organization profile.
    """

    organization_name: constr(min_length=1, max_length=100)
    industry: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None

class OrganizationProfileResponse(BaseModel):
    """
    Schema returned when retrieving an organization profile.
    """

    id: int
    user_id: int
    organization_name: str
    industry: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None

    class Config:
        orm_mode = True  # Enables reading data from SQLAlchemy ORM models

class OrganizationProfileUpdate(BaseModel):
    """
    Schema for updating an organization profile.
    All fields are optional to allow partial updates.
    """
    
    organization_name: Optional[constr(min_length=1, max_length=100)] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
