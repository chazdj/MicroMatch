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
    name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.student)
    is_active = Column(Boolean, nullable=False, default=True)
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

    # One-to-many relationship with Applications (student side)
    applications = relationship(
        "Application",
        back_populates="student",
        cascade="all, delete",
        foreign_keys="Application.student_id"
    )

    # One-to-many relationship with Feedback
    feedbacks = relationship("Feedback", back_populates="user", cascade="all, delete")

    # One-to-many relationship with Notifications
    notifications = relationship("Notification", back_populates="recipient", cascade="all, delete")

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
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationship back to User (organization)
    organization = relationship("User", back_populates="projects")

    # One-to-many relationship with Applications
    applications = relationship("Application", back_populates="project", cascade="all, delete")

    # One-to-many relationship with Feedback
    feedbacks = relationship("Feedback", back_populates="project", cascade="all, delete")

    # One-to-many relationship with Messages
    messages = relationship("ProjectMessage", back_populates="project", cascade="all, delete")

class Application(Base):
    """
    Represents a student applying to a project.
    """

    __tablename__ = "applications"

    __table_args__ = (
        UniqueConstraint("student_id", "project_id", name="uq_student_project"),
    )

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False
    )

    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    student = relationship(
        "User",
        back_populates="applications",
        foreign_keys=[student_id]
    )

    project = relationship(
        "Project",
        back_populates="applications"
    )

class Deliverable(Base):
    """
    Represents a deliverable submitted by a student
    for an accepted application.
    """

    __tablename__ = "deliverables"

    id = Column(Integer, primary_key=True, index=True)

    application_id = Column(
        Integer,
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        unique=True # prevents duplicate submissions
    )

    content = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="submitted")
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationship
    application = relationship("Application")

class Feedback(Base):
    """
    Represents feedback submitted by a student or org for a completed project.
    """
    __tablename__ = "feedback"
    __table_args__ = (UniqueConstraint("user_id", "project_id", name="uq_user_project_feedback"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)        # 1–5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="feedbacks")
    project = relationship("Project", back_populates="feedbacks")

class SystemLog(Base):
    """
    Represents a log entry for system events, such as API requests.
     Useful for monitoring and debugging."""
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # nullable for unauthenticated requests
    role = Column(String, nullable=True)
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    status_code = Column(Integer, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class Notification(Base):
    """
    Represents a notification sent to a user, such as application status updates or feedback reminders.
    """
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    recipient_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    message = Column(String, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship back to User (recipient)
    recipient = relationship("User", back_populates="notifications")

class ProjectMessage(Base):
    """
    Represents a message sent within a project context.
    Only the assigned student and owning organization may send/read messages.
    """
    __tablename__ = "project_messages"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    sender_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="messages")
    sender = relationship("User")