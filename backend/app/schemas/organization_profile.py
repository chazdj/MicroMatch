from pydantic import BaseModel, constr
from typing import Optional


# ------------------------
# Create
# ------------------------
class OrganizationProfileCreate(BaseModel):
    organization_name: constr(min_length=1, max_length=100)
    industry: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None


# ------------------------
# Read
# ------------------------
class OrganizationProfileResponse(BaseModel):
    id: int
    user_id: int
    organization_name: str
    industry: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None

    class Config:
        orm_mode = True


# ------------------------
# Update
# ------------------------
class OrganizationProfileUpdate(BaseModel):
    organization_name: Optional[constr(min_length=1, max_length=100)] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
