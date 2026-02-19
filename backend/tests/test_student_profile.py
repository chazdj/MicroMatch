import pytest
from app.models import User, StudentProfile
from app.utils.security import hash_password
from app.core.auth import create_access_token


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------

@pytest.fixture
def student_user(db_session):
    """
    Create and return a student user.
    """
    user = User(
        email="student@example.com",
        hashed_password=hash_password("password123"),
        role="student"
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def student_token(student_user):
    """
    Generate JWT token for student.
    """
    return create_access_token({
        "user_id": student_user.id,
        "role": student_user.role
    })


@pytest.fixture
def existing_student_profile(db_session, student_user):
    """
    Create a student profile for retrieval/update/delete tests.
    """
    profile = StudentProfile(
        user_id=student_user.id,
        university="Penn State University",
        major="Computer Science",
        graduation_year=2026,
        skills="Python, FastAPI",
        bio="Aspiring software engineer"
    )

    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    return profile


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------

def test_create_student_profile(client, student_token):
    """
    Ensure student can create a profile.
    """
    headers = {"Authorization": f"Bearer {student_token}"}

    payload = {
        "university": "PSU",
        "major": "CS",
        "graduation_year": 2026,
        "skills": "Python,SQL",
        "bio": "Love coding"
    }

    response = client.post("/student/profile", json=payload, headers=headers)

    assert response.status_code == 201
    assert response.json()["university"] == "PSU"


def test_get_student_profile(client, student_token, existing_student_profile):
    """
    Ensure student can retrieve their profile.
    """
    headers = {"Authorization": f"Bearer {student_token}"}

    response = client.get("/student/profile", headers=headers)

    assert response.status_code == 200
    assert "university" in response.json()


def test_update_student_profile(client, student_token, existing_student_profile):
    """
    Ensure student can update profile fields.
    """
    headers = {"Authorization": f"Bearer {student_token}"}

    response = client.put(
        "/student/profile",
        json={"bio": "Updated bio"},
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["bio"] == "Updated bio"


def test_delete_student_profile(client, student_token, existing_student_profile):
    """
    Ensure student can delete their profile.
    """
    headers = {"Authorization": f"Bearer {student_token}"}

    response = client.delete("/student/profile", headers=headers)
    assert response.status_code == 204


def test_role_restriction(client, db_session):
    """
    Ensure organization users cannot access student-only endpoints.
    """
    user = User(
        email="org@example.com",
        hashed_password=hash_password("password123"),
        role="organization"
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = create_access_token({
        "user_id": user.id,
        "role": user.role
    })

    headers = {"Authorization": f"Bearer {token}"}

    assert client.post("/student/profile", headers=headers, json={
        "university": "X",
        "major": "Y",
        "graduation_year": 2026
    }).status_code == 403

    assert client.get("/student/profile", headers=headers).status_code == 403
    assert client.put("/student/profile", headers=headers, json={"bio": "hack"}).status_code == 403
    assert client.delete("/student/profile", headers=headers).status_code == 403