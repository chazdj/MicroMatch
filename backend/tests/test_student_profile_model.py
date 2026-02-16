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
        first_name="Chastidy",
        last_name="Joanem",
        major="Computer Science",
        graduation_year=2026,
        bio="Aspiring software engineer"
    )

    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)

    assert profile.id is not None
    assert profile.user_id == user.id
    assert profile.user.email == "student@test.com"

def test_user_cannot_have_multiple_profiles(db_session):
    user = User(
        email="dup@test.com",
        hashed_password="fakehashed",
        role="student"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    profile1 = StudentProfile(
        user_id=user.id,
        first_name="A",
        last_name="B"
    )

    db_session.add(profile1)
    db_session.commit()

    profile2 = StudentProfile(
        user_id=user.id,
        first_name="C",
        last_name="D"
    )

    db_session.add(profile2)

    with pytest.raises(IntegrityError):
        db_session.commit()