import pytest
from fastapi.testclient import TestClient

from app.models import User, Project, Application, Deliverable
from app.utils.security import hash_password
from app.core.auth import create_access_token
from tests.conftest import TestingSessionLocal


# ---------------------------------------------------------
# Helper Utilities
# ---------------------------------------------------------

def get_auth_headers(user):
    token = create_access_token(
        data={"user_id": user.id}
    )
    return {
        "Authorization": f"Bearer {token}"
    }


def create_test_user(db, email, role):
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

def test_submit_deliverable_success(client):
    db = TestingSessionLocal()

    student = create_test_user(db, "student_success@test.com", "student")
    org = create_test_user(db, "org_success@test.com", "organization")

    project = create_test_project(db, org)

    application = create_test_application(
        db, student, project, status="accepted"
    )

    response = client.post(
        f"/applications/{application.id}/deliverables",
        json={"content": "Final project link"},
        headers=get_auth_headers(student)
    )

    assert response.status_code == 201

    data = response.json()
    assert data["application_id"] == application.id
    assert data["content"] == "Final project link"
    assert data["status"] == "submitted"
    assert "created_at" in data


def test_duplicate_deliverable_rejected(client):
    db = TestingSessionLocal()

    student = create_test_user(db, "student_dup@test.com", "student")
    org = create_test_user(db, "org_dup@test.com", "organization")

    project = create_test_project(db, org)

    application = create_test_application(
        db, student, project, status="accepted"
    )

    # First submission
    response1 = client.post(
        f"/applications/{application.id}/deliverables",
        json={"content": "First submission"},
        headers=get_auth_headers(student)
    )

    assert response1.status_code == 201

    # Duplicate submission
    response2 = client.post(
        f"/applications/{application.id}/deliverables",
        json={"content": "Second submission"},
        headers=get_auth_headers(student)
    )

    assert response2.status_code == 400
    assert response2.json()["detail"] == "Deliverable already submitted"

    # Ensure only one exists in DB
    deliverables = db.query(Deliverable).filter(
        Deliverable.application_id == application.id
    ).all()

    assert len(deliverables) == 1


def test_only_students_can_submit(client):
    db = TestingSessionLocal()

    student = create_test_user(db, "student_auth@test.com", "student")
    org = create_test_user(db, "org_auth@test.com", "organization")

    project = create_test_project(db, org)

    application = create_test_application(
        db, student, project, status="accepted"
    )

    response = client.post(
        f"/applications/{application.id}/deliverables",
        json={"content": "Test content"},
        headers=get_auth_headers(org)  # organization trying
    )

    assert response.status_code == 403


def test_application_not_found(client):
    db = TestingSessionLocal()

    student = create_test_user(db, "student_404@test.com", "student")

    response = client.post(
        "/applications/999999/deliverables",
        json={"content": "Test"},
        headers=get_auth_headers(student)
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Application not found"


def test_only_owner_can_submit(client):
    db = TestingSessionLocal()

    student1 = create_test_user(db, "student1@test.com", "student")
    student2 = create_test_user(db, "student2@test.com", "student")
    org = create_test_user(db, "org_owner@test.com", "organization")

    project = create_test_project(db, org)

    application = create_test_application(
        db, student1, project, status="accepted"
    )

    # student2 tries to submit for student1's application
    response = client.post(
        f"/applications/{application.id}/deliverables",
        json={"content": "Hacked submission"},
        headers=get_auth_headers(student2)
    )

    assert response.status_code == 403


def test_application_must_be_accepted(client):
    db = TestingSessionLocal()

    student = create_test_user(db, "student_status@test.com", "student")
    org = create_test_user(db, "org_status@test.com", "organization")

    project = create_test_project(db, org)

    # NOT accepted
    application = create_test_application(
        db, student, project, status="pending"
    )

    response = client.post(
        f"/applications/{application.id}/deliverables",
        json={"content": "Should fail"},
        headers=get_auth_headers(student)
    )

    assert response.status_code == 400
    assert "accepted applications" in response.json()["detail"]


def test_empty_deliverable_rejected(client):
    db = TestingSessionLocal()

    student = create_test_user(db, "student_empty@test.com", "student")
    org = create_test_user(db, "org_empty@test.com", "organization")

    project = create_test_project(db, org)

    application = create_test_application(
        db, student, project, status="accepted"
    )

    response = client.post(
        f"/applications/{application.id}/deliverables",
        json={"content": "   "},  # empty
        headers=get_auth_headers(student)
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Deliverable content cannot be empty"


def test_deliverable_persistence(client):
    """
    Ensures deliverable is actually stored in DB correctly.
    """
    db = TestingSessionLocal()

    student = create_test_user(db, "student_db@test.com", "student")
    org = create_test_user(db, "org_db@test.com", "organization")

    project = create_test_project(db, org)

    application = create_test_application(
        db, student, project, status="accepted"
    )

    response = client.post(
        f"/applications/{application.id}/deliverables",
        json={"content": "Persistent content"},
        headers=get_auth_headers(student)
    )

    assert response.status_code == 201

    deliverable = db.query(Deliverable).filter(
        Deliverable.application_id == application.id
    ).first()

    assert deliverable is not None
    assert deliverable.content == "Persistent content"
    assert deliverable.status == "submitted"