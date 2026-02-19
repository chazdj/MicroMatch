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

class StudentProfileRead(StudentProfileBase):
    """
    Schema returned when retrieving a student profile.
    """
    id: int
    user_id: int