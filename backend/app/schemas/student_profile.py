from pydantic import BaseModel, ConfigDict
from typing import Optional

class StudentProfileBase(BaseModel):
    """
    Shared attributes for student profile creation and reading.
    """
     
    university: str
    major: str
    graduation_year: int
    skills: Optional[str] = None
    bio: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)  # Enables ORM compatibility

class StudentProfileCreate(StudentProfileBase):
    """
    Schema used when creating a student profile.
    """
    pass

class StudentProfileUpdate(BaseModel):
    """
    Schema used when updating a student profile.
    All fields are optional for partial updates.
    """
    
    university: Optional[str] = None
    major: Optional[str] = None
    graduation_year: Optional[int] = None
    skills: Optional[str] = None
    bio: Optional[str] = None

class StudentProfileEnhance(BaseModel):
    """
    Schema for PUT /profiles/student/enhance.
    All enhancement fields are optional — only provided fields are updated.
    """
    portfolio_links: Optional[str] = None   
    model_config = ConfigDict(from_attributes=True)

class StudentProfileRead(StudentProfileBase):
    """
    Schema returned when retrieving a student profile.
    Includes base fields plus computed enhancement fields.
    """
    id: int
    user_id: int

    # Stored enhancement fields
    portfolio_links: Optional[str] = None
    badges: Optional[str] = None

    # Computed fields (injected by the router, not stored directly)
    completed_projects: Optional[int] = None
    average_rating: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)