from fastapi.testclient import TestClient
from app.models import User, Project, Application, Deliverable
from app.utils.security import hash_password
from app.core.auth import create_access_token
from tests.conftest import TestingSessionLocal


# ----------------------------
# Helpers
# ----------------------------

def get_auth_headers(user):
    token = create_access_token({"user_id": user.id})
    return {"Authorization": f"Bearer {token}"}


def create_user(db, email, role):
    user = User(
        email=email,
        hashed_password=hash_password("password"),
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_project(db, org):
    project = Project(
        organization_id=org.id,
        title="Test",
        description="Desc",
        status="open"
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def create_application(db, student, project):
    app = Application(
        student_id=student.id,
        project_id=project.id,
        status="accepted"
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    return app


def create_deliverable(db, application):
    d = Deliverable(
        application_id=application.id,
        content="test",
        status="submitted"
    )
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


# ----------------------------
# Tests
# ----------------------------

def test_accept_deliverable(client):
    db = TestingSessionLocal()

    org = create_user(db, "org@test.com", "organization")
    student = create_user(db, "student@test.com", "student")

    project = create_project(db, org)
    app = create_application(db, student, project)
    d = create_deliverable(db, app)

    res = client.put(
        f"/deliverables/{d.id}/review",
        json={"status": "accepted"},
        headers=get_auth_headers(org)
    )

    assert res.status_code == 200
    assert res.json()["status"] == "accepted"


def test_reject_deliverable(client):
    db = TestingSessionLocal()

    org = create_user(db, "org2@test.com", "organization")
    student = create_user(db, "student2@test.com", "student")

    project = create_project(db, org)
    app = create_application(db, student, project)
    d = create_deliverable(db, app)

    res = client.put(
        f"/deliverables/{d.id}/review",
        json={"status": "rejected"},
        headers=get_auth_headers(org)
    )

    assert res.status_code == 200
    assert res.json()["status"] == "rejected"


def test_prevent_double_review(client):
    db = TestingSessionLocal()

    org = create_user(db, "org3@test.com", "organization")
    student = create_user(db, "student3@test.com", "student")

    project = create_project(db, org)
    app = create_application(db, student, project)
    d = create_deliverable(db, app)

    # First review
    client.put(
        f"/deliverables/{d.id}/review",
        json={"status": "accepted"},
        headers=get_auth_headers(org)
    )

    # Second review
    res = client.put(
        f"/deliverables/{d.id}/review",
        json={"status": "rejected"},
        headers=get_auth_headers(org)
    )

    assert res.status_code == 400
    assert res.json()["detail"] == "Deliverable already reviewed"


def test_wrong_org_cannot_review(client):
    db = TestingSessionLocal()

    org1 = create_user(db, "org1@test.com", "organization")
    org2 = create_user(db, "org2@test.com", "organization")
    student = create_user(db, "student@test.com", "student")

    project = create_project(db, org1)
    app = create_application(db, student, project)
    d = create_deliverable(db, app)

    res = client.put(
        f"/deliverables/{d.id}/review",
        json={"status": "accepted"},
        headers=get_auth_headers(org2)
    )

    assert res.status_code == 403


def test_deliverable_not_found(client):
    db = TestingSessionLocal()

    org = create_user(db, "org@test.com", "organization")

    res = client.put(
        "/deliverables/999/review",
        json={"status": "accepted"},
        headers=get_auth_headers(org)
    )

    assert res.status_code == 404