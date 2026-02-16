from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="user")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    # student_profile = relationship(
    #     "StudentProfile", 
    #     back_populates="user",
    #     uselist=False,
    #     cascade="all, delete"
    # )

    # organization_profile = relationship(
    #     "OrganizationProfile", 
    #     back_populates="user",
    #     uselist=False,
    #     cascade="all, delete"
    # )