# tests/test_sprint1_workflow.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import User, Project
from app.utils.security import hash_password

@pytest.fixture
def client():
    """
    Provides a FastAPI TestClient instance for testing.
    """
    with TestClient(app) as c:
        yield c


def test_sprint1_end_to_end(client):
    """
    End-to-End Test: Sprint 1 Workflow
    
    Steps:
    1. Register an organization user
    2. Register a student user
    3. Organization posts a project
    4. Student logs in and views project list

    Checks:
    - Registration works
    - JWT tokens are returned
    - Role-based access works
    - Projects are visible to students
    """
    # ----------------------------------------
    # Step 1: Register Organization
    # ----------------------------------------
    org_data = {
        "email": "org@example.com",
        "password": "password123",
        "role": "organization"
    }
    response = client.post("/auth/register", json=org_data)
    assert response.status_code == 201
    assert response.json()["email"] == org_data["email"]

    # Log in as organization to get token
    response = client.post("/auth/login", json={
        "email": org_data["email"],
        "password": org_data["password"]
    })
    assert response.status_code == 200
    org_token = response.json()["access_token"]
    assert org_token

    # ----------------------------------------
    # Step 2: Register Student
    # ----------------------------------------
    student_data = {
        "email": "student@example.com",
        "password": "password123",
        "role": "student"
    }
    response = client.post("/auth/register", json=student_data)
    assert response.status_code == 201
    assert response.json()["email"] == student_data["email"]

    # Log in as student to get token
    response = client.post("/auth/login", json={
        "email": student_data["email"],
        "password": student_data["password"]
    })
    assert response.status_code == 200
    student_token = response.json()["access_token"]
    assert student_token

    # ----------------------------------------
    # Step 3: Organization posts a project
    # ----------------------------------------
    project_data = {
        "title": "Test Project",
        "description": "End-to-end workflow test project",
        "required_skills": "Python,FastAPI",
        "duration": "1 month"
    }
    response = client.post(
        "/projects",
        json=project_data,
        headers={"Authorization": f"Bearer {org_token}"}
    )
    assert response.status_code == 201
    project_id = response.json()["id"]
    assert response.json()["title"] == project_data["title"]

    # ----------------------------------------
    # Step 4: Student fetches list of projects
    # ----------------------------------------
    response = client.get(
        "/projects",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 200
    projects = response.json()
    # Check that our project is in the list
    assert any(p["id"] == project_id for p in projects)
    assert any("Test Project" in p["title"] for p in projects)

    # ----------------------------------------
    # Step 5: Attempt unauthorized project creation (student should fail)
    # ----------------------------------------
    response = client.post(
        "/projects",
        json=project_data,
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 403  # Forbidden