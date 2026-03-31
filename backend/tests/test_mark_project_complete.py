from app.models import User, Project, Application, Deliverable
from app.utils.security import hash_password
from app.core.auth import create_access_token
from tests.conftest import TestingSessionLocal


# ----------------------------
# Helpers
# ----------------------------

def get_auth_headers(user):
    token = create_access_token(data={"user_id": user.id})
    return {"Authorization": f"Bearer {token}"}


def create_user(db, email, role):
    user = User(
        email=email,
        hashed_password=hash_password("password123"),
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_project(db, org, status="open"):
    project = Project(
        organization_id=org.id,
        title="Test Project",
        description="Test Description",
        status=status
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def create_application(db, student, project, status="accepted"):
    application = Application(
        student_id=student.id,
        project_id=project.id,
        status=status
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


def create_deliverable(db, application, status="accepted"):
    deliverable = Deliverable(
        application_id=application.id,
        content="Final work submitted.",
        status=status
    )
    db.add(deliverable)
    db.commit()
    db.refresh(deliverable)
    return deliverable


# ----------------------------
# TC-US12-01: Successful Completion
# ----------------------------

def test_mark_project_complete_success(client):
    """
    TC-US12-01 – Organization marks project complete when deliverable is accepted.
    Expected: HTTP 200, project status = 'completed', completed_at set.
    """
    db = TestingSessionLocal()
    org = create_user(db, "org@test.com", "organization")
    student = create_user(db, "student@test.com", "student")
    project = create_project(db, org, status="open")
    application = create_application(db, student, project, status="accepted")
    create_deliverable(db, application, status="accepted")

    response = client.put(
        f"/projects/{project.id}/complete",
        headers=get_auth_headers(org)
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["completed_at"] is not None


def test_mark_project_complete_response_schema(client):
    """
    TC-US12-01 – Validates response payload contains expected fields.
    """
    db = TestingSessionLocal()
    org = create_user(db, "org_schema@test.com", "organization")
    student = create_user(db, "student_schema@test.com", "student")
    project = create_project(db, org)
    application = create_application(db, student, project)
    create_deliverable(db, application, status="accepted")

    response = client.put(
        f"/projects/{project.id}/complete",
        headers=get_auth_headers(org)
    )

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "status" in data
    assert "completed_at" in data
    assert data["status"] == "completed"


# ----------------------------
# TC-US12-02: Prevent Premature Completion
# ----------------------------

def test_cannot_complete_with_pending_deliverable(client):
    """
    TC-US12-02 – Project cannot be completed if deliverable is still pending.
    Expected: HTTP 400.
    """
    db = TestingSessionLocal()
    org = create_user(db, "org2@test.com", "organization")
    student = create_user(db, "student2@test.com", "student")
    project = create_project(db, org)
    application = create_application(db, student, project)
    create_deliverable(db, application, status="submitted")  # not accepted

    response = client.put(
        f"/projects/{project.id}/complete",
        headers=get_auth_headers(org)
    )

    assert response.status_code == 400
    assert "accepted" in response.json()["detail"].lower()


def test_cannot_complete_with_rejected_deliverable(client):
    """
    TC-US12-02 – Project cannot be completed if deliverable was rejected.
    Expected: HTTP 400.
    """
    db = TestingSessionLocal()
    org = create_user(db, "org3@test.com", "organization")
    student = create_user(db, "student3@test.com", "student")
    project = create_project(db, org)
    application = create_application(db, student, project)
    create_deliverable(db, application, status="rejected")

    response = client.put(
        f"/projects/{project.id}/complete",
        headers=get_auth_headers(org)
    )

    assert response.status_code == 400


def test_cannot_complete_project_with_no_deliverable(client):
    """
    TC-US12-02 – Project cannot be completed if no deliverable exists at all.
    Expected: HTTP 400.
    """
    db = TestingSessionLocal()
    org = create_user(db, "org4@test.com", "organization")
    project = create_project(db, org)

    response = client.put(
        f"/projects/{project.id}/complete",
        headers=get_auth_headers(org)
    )

    assert response.status_code == 400


def test_project_status_unchanged_on_failed_completion(client):
    """
    TC-US12-02 – Project status remains unchanged after a failed complete attempt.
    """
    db = TestingSessionLocal()
    org = create_user(db, "org5@test.com", "organization")
    student = create_user(db, "student5@test.com", "student")
    project = create_project(db, org, status="open")
    application = create_application(db, student, project)
    create_deliverable(db, application, status="submitted")

    client.put(f"/projects/{project.id}/complete", headers=get_auth_headers(org))

    db.refresh(project)
    assert project.status == "open"


# ----------------------------
# TC-US12-03: Unauthorized Role
# ----------------------------

def test_student_cannot_complete_project(client):
    """
    TC-US12-03 – Student role cannot call the complete endpoint.
    Expected: HTTP 403.
    """
    db = TestingSessionLocal()
    org = create_user(db, "org6@test.com", "organization")
    student = create_user(db, "student6@test.com", "student")
    project = create_project(db, org)
    application = create_application(db, student, project)
    create_deliverable(db, application, status="accepted")

    response = client.put(
        f"/projects/{project.id}/complete",
        headers=get_auth_headers(student)
    )

    assert response.status_code == 403


def test_wrong_org_cannot_complete_project(client):
    """
    TC-US12-03 – An org that does not own the project cannot complete it.
    Expected: HTTP 403.
    """
    db = TestingSessionLocal()
    org1 = create_user(db, "org_owner@test.com", "organization")
    org2 = create_user(db, "org_intruder@test.com", "organization")
    student = create_user(db, "student7@test.com", "student")
    project = create_project(db, org1)
    application = create_application(db, student, project)
    create_deliverable(db, application, status="accepted")

    response = client.put(
        f"/projects/{project.id}/complete",
        headers=get_auth_headers(org2)
    )

    assert response.status_code == 403


def test_complete_project_not_found(client):
    """
    TC-US12-03 – Attempting to complete a non-existent project.
    Expected: HTTP 404.
    """
    db = TestingSessionLocal()
    org = create_user(db, "org_missing@test.com", "organization")

    response = client.put(
        "/projects/999999/complete",
        headers=get_auth_headers(org)
    )

    assert response.status_code == 404