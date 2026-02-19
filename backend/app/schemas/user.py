from pydantic import BaseModel, EmailStr
from enum import Enum

class UserRole(str, Enum):
    """
    Enum representing allowed user roles in the system.
    """

    student = "student"
    organization = "organization"
    admin = "admin"

class UserCreate(BaseModel):
    """
    Schema for registering a new user.
    """

    email: EmailStr
    password: str
    role: UserRole

class LoginRequest(BaseModel):
    """
    Schema for login requests.
    """

    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    """
    Schema returned after successful authentication.
    """

    access_token: str
    token_type: str = "bearer"