import pytest
from app.models import User, StudentProfile
from sqlalchemy.exc import IntegrityError


def test_create_student_profile(db_session):
    """
    Ensure a student profile can be created and linked to its user.
    """
    user = User(
        email="student@test.com",
        hashed_password="fakehashed",
        role="student"
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

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

    assert profile.user.email == "student@test.com"
    assert profile.major == "Computer Science"


def test_user_cannot_have_multiple_profiles(db_session):
    """
    Ensure unique constraint prevents multiple profiles per student.
    """
    user = User(
        email="dup@test.com",
        hashed_password="fakehashed",
        role="student"
    )

    db_session.add(user)
    db_session.commit()

    profile1 = StudentProfile(
        user_id=user.id,
        university="PSU",
        major="IST",
        graduation_year=2025
    )

    db_session.add(profile1)
    db_session.commit()

    profile2 = StudentProfile(
        user_id=user.id,
        university="Another University",
        major="Another Major",
        graduation_year=2030
    )

    db_session.add(profile2)

    with pytest.raises(IntegrityError):
        db_session.commit()