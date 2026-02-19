from sqlalchemy import *
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
from app.schemas.user import UserRole

class User(Base):
    """
    Represents a system user.
    Can have role: student, organization, or admin.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.student)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # One-to-one relationship with StudentProfile
    student_profile = relationship(
        "StudentProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete"
    )

    # One-to-one relationship with OrganizationProfile
    organization_profile = relationship(
        "OrganizationProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete"
    )

    # One-to-many relationship with Projects
    projects = relationship(
        "Project",
        back_populates="organization",
        cascade="all, delete"
    )

class StudentProfile(Base):
    """
    Represents additional information for student users.
    Each student can only have one profile.
    """

    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)

    # Foreign key to users table
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    university = Column(String, nullable=False)
    major = Column(String, nullable=False)
    graduation_year = Column(Integer, nullable=False)

    # Skills stored as comma-separated string
    skills = Column(String, nullable=True)

    bio = Column(Text, nullable=True)

    # Relationship back to User
    user = relationship("User", back_populates="student_profile")

class OrganizationProfile(Base):
    """
    Represents additional information for organization users.
    """

    __tablename__ = "organization_profiles"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        unique=True
    )

    organization_name = Column(String, nullable=False)
    industry = Column(String, nullable=True)
    website = Column(String, nullable=True)
    description = Column(String, nullable=True)

    user = relationship("User", back_populates="organization_profile")

class Project(Base):
    """
    Represents a project created by an organization.
    """

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)

    # Linked to organization user
    organization_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)

    # Stored as comma-separated string
    required_skills = Column(String, nullable=True)

    duration = Column(String, nullable=True)
    status = Column(String, nullable=False, default="open")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship back to User (organization)
    organization = relationship("User", back_populates="projects")