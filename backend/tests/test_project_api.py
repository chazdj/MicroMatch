import pytest
from app.models import User
from app.core.auth import create_access_token
from app.schemas.user import UserRole

@pytest.fixture
def org_user(db_session):
    user = User(
        email="org@example.com", 
        hashed_password="hashed", 
        role=UserRole.organization
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def org_token(org_user):
    return create_access_token({"user_id": org_user.id, "role": org_user.role.value})

@pytest.fixture
def student_user(db_session):
    user = User(
        email="student@example.com", 
        hashed_password="hashed", 
        role=UserRole.student
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def student_token(student_user):
    return create_access_token({"user_id": student_user.id, "role": student_user.role.value})

def test_create_project_valid(client, org_token):
    headers = {"Authorization": f"Bearer {org_token}"}
    payload = {
        "title": "New Micro-Internship",
        "description": "Test project for backend",
        "required_skills": "Python,FastAPI",
        "duration": "2 weeks"
    }
    response = client.post("/projects", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["status"] == "open"

def test_create_project_missing_fields(client, org_token):
    headers = {"Authorization": f"Bearer {org_token}"}
    payload = {
        "description": "Missing title field"
    }
    response = client.post("/projects", json=payload, headers=headers)
    assert response.status_code == 422  # validation error

def test_student_cannot_create_project(client, student_token):
    headers = {"Authorization": f"Bearer {student_token}"}
    payload = {
        "title": "Unauthorized Project",
        "description": "Student should not create"
    }
    response = client.post("/projects", json=payload, headers=headers)
    assert response.status_code == 403  # forbidden
