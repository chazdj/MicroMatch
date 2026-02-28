import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import Application, Project, User
from app.database import Base
from app.utils.security import hash_password
from app.core.auth import create_access_token

from tests.conftest import TestingSessionLocal, engine


# ---------------------------------------------------------
# Helper Utilities
# ---------------------------------------------------------

def get_auth_headers(user):
    """
    Generate valid JWT authorization headers
    for testing protected endpoints.
    """

    token = create_access_token(
        data={"user_id": user.id}
    )

    return {
        "Authorization": f"Bearer {token}"
    }


# ---------------------------------------------------------
# Fixtures Setup Helpers
# ---------------------------------------------------------

def create_test_user(db, email, role):
    """
    Create a test user.
    """

    user = User(
        email=email,
        hashed_password=hash_password("password123"),
        role=role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def create_test_project(db, org_user):
    """
    Create project owned by organization user.
    """

    project = Project(
        organization_id=org_user.id,
        title="Test Project",
        description="Test Description",
        status="open"
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


def create_test_application(db, student, project, status="pending"):
    """
    Create application record for testing.
    """

    application = Application(
        student_id=student.id,
        project_id=project.id,
        status=status
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    return application


# ---------------------------------------------------------
# Tests
# ---------------------------------------------------------

def test_accept_application_success(client):
    """
    Organization successfully accepts pending application.
    """

    db = TestingSessionLocal()

    org_user = create_test_user(db, "org@test.com", "organization")
    student_user = create_test_user(db, "student@test.com", "student")

    project = create_test_project(db, org_user)

    application = create_test_application(
        db,
        student_user,
        project,
        status="pending"
    )

    response = client.patch(
        f"/applications/{application.id}/status",
        json={"status": "accepted"},
        headers=get_auth_headers(org_user)
    )

    assert response.status_code == 200
    assert response.json()["status"] == "accepted"


def test_reject_application_success(client):
    """
    Organization rejects pending application.
    """

    db = TestingSessionLocal()

    org_user = create_test_user(db, "org2@test.com", "organization")
    student_user = create_test_user(db, "student2@test.com", "student")

    project = create_test_project(db, org_user)

    application = create_test_application(
        db,
        student_user,
        project,
        status="pending"
    )

    response = client.patch(
        f"/applications/{application.id}/status",
        json={"status": "rejected"},
        headers=get_auth_headers(org_user)
    )

    assert response.status_code == 200
    assert response.json()["status"] == "rejected"


def test_invalid_status_rejected(client):
    """
    Test rejection of invalid status value.
    """

    db = TestingSessionLocal()

    org_user = create_test_user(db, "org3@test.com", "organization")
    student_user = create_test_user(db, "student3@test.com", "student")

    project = create_test_project(db, org_user)

    application = create_test_application(
        db,
        student_user,
        project
    )

    response = client.patch(
        f"/applications/{application.id}/status",
        json={"status": "invalid_status"},
        headers=get_auth_headers(org_user)
    )

    assert response.status_code == 400


def test_cannot_reupdate_application(client):
    """
    Applications cannot be updated once accepted/rejected.
    """

    db = TestingSessionLocal()

    org_user = create_test_user(db, "org4@test.com", "organization")
    student_user = create_test_user(db, "student4@test.com", "student")

    project = create_test_project(db, org_user)

    application = create_test_application(
        db,
        student_user,
        project,
        status="accepted"
    )

    response = client.patch(
        f"/applications/{application.id}/status",
        json={"status": "rejected"},
        headers=get_auth_headers(org_user)
    )

    assert response.status_code == 400


def test_unauthorized_organization_cannot_update(client):
    """
    Organization that does not own project cannot update application.
    """

    db = TestingSessionLocal()

    org1 = create_test_user(db, "owner@test.com", "organization")
    org2 = create_test_user(db, "intruder@test.com", "organization")

    student = create_test_user(db, "student5@test.com", "student")

    project = create_test_project(db, org1)

    application = create_test_application(
        db,
        student,
        project
    )

    response = client.patch(
        f"/applications/{application.id}/status",
        json={"status": "accepted"},
        headers=get_auth_headers(org2)
    )

    assert response.status_code == 403

def test_project_ownership_enforced(client):
    """
    Organization cannot modify applications for projects they do not own.
    """
    db = TestingSessionLocal()

    # Create two organizations
    owner_org = create_test_user(db, "owner_security@test.com", "organization")
    intruder_org = create_test_user(db, "intruder_security@test.com", "organization")

    student = create_test_user(db, "student_security@test.com", "student")

    # Project belongs to owner_org
    project = create_test_project(db, owner_org)

    # Application exists
    application = create_test_application(
        db,
        student,
        project,
        status="pending"
    )

    # Intruder organization attempts update
    response = client.patch(
        f"/applications/{application.id}/status",
        json={"status": "accepted"},
        headers=get_auth_headers(intruder_org)
    )

    assert response.status_code == 403

def test_application_not_found(client):
    """
    Test updating a non-existent application.
    """

    db = TestingSessionLocal()

    org_user = create_test_user(db, "org_missing@test.com", "organization")

    # Use a large ID that is unlikely to exist
    invalid_application_id = 999999

    response = client.patch(
        f"/applications/{invalid_application_id}/status",
        json={"status": "accepted"},
        headers=get_auth_headers(org_user)
    )

    assert response.status_code == 404

def test_status_transition_lock(client):
    """
    Ensure accepted/rejected applications cannot be modified again.
    """
    db = TestingSessionLocal()

    org_user = create_test_user(db, "transition_org@test.com", "organization")
    student = create_test_user(db, "transition_student@test.com", "student")

    project = create_test_project(db, org_user)

    application = create_test_application(
        db,
        student,
        project,
        status="accepted"
    )

    response = client.patch(
        f"/applications/{application.id}/status",
        json={"status": "accepted"},
        headers=get_auth_headers(org_user)
    )

    assert response.status_code == 400

def test_accept_application_response_schema(client):
    """
    Validate response payload structure.
    """
    db = TestingSessionLocal()

    org_user = create_test_user(db, "schema_org@test.com", "organization")
    student = create_test_user(db, "schema_student@test.com", "student")

    project = create_test_project(db, org_user)

    application = create_test_application(
        db,
        student,
        project
    )

    response = client.patch(
        f"/applications/{application.id}/status",
        json={"status": "accepted"},
        headers=get_auth_headers(org_user)
    )

    data = response.json()

    assert "status" in data
    assert "id" in data
    assert response.status_code == 200