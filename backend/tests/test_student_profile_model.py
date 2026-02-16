import pytest
from app.models import User, StudentProfile
from sqlalchemy.exc import IntegrityError


def test_create_student_profile(db_session):
    # Create a user first
    user = User(
        email="student@test.com",
        hashed_password="fakehashed",
        role="student"
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Create student profile
    profile = StudentProfile(
        user_id=user.id,
        university="Penn State University", 
        major="Computer Science", 
        graduation_year=2026, 
        skills="Python, FastAPI", 
        bio="Aspiring software engineer"
    )

    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)

    assert profile.id is not None
    assert profile.user_id == user.id
    assert profile.user.email == "student@test.com"
    assert profile.university == "Penn State University" 
    assert profile.major == "Computer Science" 
    assert profile.graduation_year == 2026 
    assert profile.skills == "Python, FastAPI" 
    assert profile.bio == "Aspiring software engineer"

def test_user_cannot_have_multiple_profiles(db_session):
    user = User(
        email="dup@test.com",
        hashed_password="fakehashed",
        role="student"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Create first profile
    profile1 = StudentProfile(
        user_id=user.id,
        university="PSU", 
        major="IST", 
        graduation_year=2025
    )

    db_session.add(profile1)
    db_session.commit()

    # Second profile for same user should fail
    profile2 = StudentProfile(
        user_id=user.id,
        university="Another University", 
        major="Another Major", 
        graduation_year=2030
    )

    db_session.add(profile2)

    with pytest.raises(IntegrityError):
        db_session.commit()