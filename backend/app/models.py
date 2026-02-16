from sqlalchemy import *
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
from app.schemas.user import UserRole

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.student)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    student_profile = relationship(
        "StudentProfile", 
        back_populates="user",
        uselist=False,
        cascade="all, delete"
    )

    organization_profile = relationship(
        "OrganizationProfile", 
        back_populates="user",
        uselist=False,
        cascade="all, delete"
    )

class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    university = Column(String, nullable=False) 
    major = Column(String, nullable=False) 
    graduation_year = Column(Integer, nullable=False) 
    
    # Store skills as a comma‑separated string 
    skills = Column(String, nullable=True) 
    
    bio = Column(Text, nullable=True) 

    # Relationship back to User 
    user = relationship("User", back_populates="student_profile")

class OrganizationProfile(Base):
    __tablename__ = "organization_profiles"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)

    organization_name = Column(String, nullable=False)
    industry = Column(String, nullable=True)
    website = Column(String, nullable=True)
    description = Column(String, nullable=True)

    user = relationship("User", back_populates="organization_profile")
