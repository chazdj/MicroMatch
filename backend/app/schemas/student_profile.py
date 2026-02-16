from pydantic import BaseModel, ConfigDict
from typing import Optional

class StudentProfileBase(BaseModel):
    university: str
    major: str
    graduation_year: int
    skills: Optional[str] = None
    bio: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)  # supports ORM objects

class StudentProfileCreate(StudentProfileBase):
    pass

class StudentProfileUpdate(BaseModel):
    university: Optional[str] = None
    major: Optional[str] = None
    graduation_year: Optional[int] = None
    skills: Optional[str] = None
    bio: Optional[str] = None

class StudentProfileRead(StudentProfileBase):
    id: int
    user_id: int