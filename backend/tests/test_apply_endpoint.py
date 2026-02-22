import pytest
from app.models import User, Project
from app.schemas.user import UserRole
from app.core.dependencies import require_role, get_current_user
from app.main import app

student_role_dep = require_role("student") 
organization_role_dep = require_role("organization")

def override_auth_dependency(user): 
    app.dependency_overrides[get_current_user] = lambda: user

# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------

def create_student(db):
    """
    Creates and returns a student user.
    """
    student = User(
        email="student@test.com",
        hashed_password="hashed",
        role=UserRole.student
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def create_org(db):
    """
    Creates and returns an organization user.
    """
    org = User(
        email="org@test.com",
        hashed_password="hashed",
        role=UserRole.organization
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


def create_project(db, org):
    """
    Creates and returns a project owned by the organization.
    """
    project = Project(
        organization_id=org.id,
        title="Test Project",
        description="Test Description"
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


# ---------------------------------------------------------
# Test Cases
# ---------------------------------------------------------

def test_student_can_apply(client, db_session):
    """
    Ensures a student can successfully apply to a project.
    """

    student = create_student(db_session)
    org = create_org(db_session)
    project = create_project(db_session, org)

    override_auth_dependency(student)

    response = client.post(
        "/applications",
        json={"project_id": project.id}
    )

    assert response.status_code == 201
    data = response.json()

    assert data["student_id"] == student.id
    assert data["project_id"] == project.id
    assert data["status"] == "pending"


def test_duplicate_application_blocked(client, db_session):
    """
    Ensures a student cannot apply to the same project twice.
    """

    student = create_student(db_session)
    org = create_org(db_session)
    project = create_project(db_session, org)

    override_auth_dependency(student)

    client.post("/applications", json={"project_id": project.id})
    response = client.post("/applications", json={"project_id": project.id})

    assert response.status_code == 400
    assert "already applied" in response.json()["detail"]


def test_project_not_found(client, db_session):
    """
    Ensures applying to a non-existent project returns 404.
    """

    student = create_student(db_session)

    override_auth_dependency(student)

    response = client.post("/applications", json={"project_id": 999})

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_only_students_can_apply(client, db_session):
    """
    Ensures non-student users cannot apply to projects.
    """

    org = create_org(db_session)

    override_auth_dependency(org)

    response = client.post("/applications", json={"project_id": 1})

    # Since require_role("student") is used,
    # FastAPI will return 403 if role mismatch
    assert response.status_code in (401, 403)