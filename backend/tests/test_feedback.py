from app.models import User, Project, Application, Deliverable, Feedback
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


def create_project(db, org, status="completed"):
    project = Project(
        organization_id=org.id,
        title="Completed Project",
        description="A finished project.",
        status=status
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


# ----------------------------
# TC-US13-01: Successful Feedback Submission
# ----------------------------

def test_submit_feedback_success(client):
    """
    TC-US13-01 – Student submits feedback for a completed project.
    Expected: HTTP 201, feedback stored with correct fields.
    """
    db = TestingSessionLocal()
    org = create_user(db, "org@test.com", "organization")
    student = create_user(db, "student@test.com", "student")
    project = create_project(db, org, status="completed")

    response = client.post(
        "/feedback",
        json={"project_id": project.id, "rating": 5, "comment": "Great experience!"},
        headers=get_auth_headers(student)
    )

    assert response.status_code == 201
    data = response.json()
    assert data["rating"] == 5
    assert data["comment"] == "Great experience!"
    assert data["project_id"] == project.id
    assert data["user_id"] == student.id


def test_submit_feedback_response_schema(client):
    """
    TC-US13-01 – Validates response payload structure.
    """
    db = TestingSessionLocal()
    org = create_user(db, "org_schema@test.com", "organization")
    student = create_user(db, "student_schema@test.com", "student")
    project = create_project(db, org)

    response = client.post(
        "/feedback",
        json={"project_id": project.id, "rating": 4, "comment": "Good."},
        headers=get_auth_headers(student)
    )

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert "user_id" in data
    assert "project_id" in data
    assert "rating" in data
    assert "created_at" in data


def test_submit_feedback_without_comment(client):
    """
    TC-US13-01 – Comment field is optional; submission succeeds without it.
    """
    db = TestingSessionLocal()
    org = create_user(db, "org_nocomment@test.com", "organization")
    student = create_user(db, "student_nocomment@test.com", "student")
    project = create_project(db, org)

    response = client.post(
        "/feedback",
        json={"project_id": project.id, "rating": 3},
        headers=get_auth_headers(student)
    )

    assert response.status_code == 201


def test_feedback_visible_on_project(client):
    """
    TC-US13-01 – Submitted feedback is retrievable via GET /feedback/{project_id}.
    """
    db = TestingSessionLocal()
    org = create_user(db, "org_get@test.com", "organization")
    student = create_user(db, "student_get@test.com", "student")
    project = create_project(db, org)

    client.post(
        "/feedback",
        json={"project_id": project.id, "rating": 5, "comment": "Excellent!"},
        headers=get_auth_headers(student)
    )

    response = client.get(
        f"/feedback/{project.id}",
        headers=get_auth_headers(student)
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["rating"] == 5


# ----------------------------
# TC-US13-02: Prevent Feedback Before Completion
# ----------------------------

def test_cannot_submit_feedback_for_open_project(client):
    """
    TC-US13-02 – Feedback cannot be submitted for a project that is still open.
    Expected: HTTP 400.
    """
    db = TestingSessionLocal()
    org = create_user(db, "org2@test.com", "organization")
    student = create_user(db, "student2@test.com", "student")
    project = create_project(db, org, status="open")

    response = client.post(
        "/feedback",
        json={"project_id": project.id, "rating": 4, "comment": "Too early."},
        headers=get_auth_headers(student)
    )

    assert response.status_code == 400
    assert "completed" in response.json()["detail"].lower()


def test_cannot_submit_feedback_for_in_progress_project(client):
    """
    TC-US13-02 – Feedback rejected when project status is in_progress.
    Expected: HTTP 400.
    """
    db = TestingSessionLocal()
    org = create_user(db, "org3@test.com", "organization")
    student = create_user(db, "student3@test.com", "student")
    project = create_project(db, org, status="in_progress")

    response = client.post(
        "/feedback",
        json={"project_id": project.id, "rating": 2},
        headers=get_auth_headers(student)
    )

    assert response.status_code == 400


def test_invalid_rating_rejected(client):
    """
    TC-US13-02 – Rating must be between 1 and 5. Out-of-range values are rejected.
    Expected: HTTP 422.
    """
    db = TestingSessionLocal()
    org = create_user(db, "org_rating@test.com", "organization")
    student = create_user(db, "student_rating@test.com", "student")
    project = create_project(db, org)

    response = client.post(
        "/feedback",
        json={"project_id": project.id, "rating": 10},
        headers=get_auth_headers(student)
    )

    assert response.status_code == 422


# ----------------------------
# TC-US13-03: Duplicate Feedback Prevention
# ----------------------------

def test_duplicate_feedback_rejected(client):
    """
    TC-US13-03 – A user cannot submit feedback more than once for the same project.
    Expected: HTTP 400 on second submission.
    """
    db = TestingSessionLocal()
    org = create_user(db, "org4@test.com", "organization")
    student = create_user(db, "student4@test.com", "student")
    project = create_project(db, org)

    # First submission
    r1 = client.post(
        "/feedback",
        json={"project_id": project.id, "rating": 5, "comment": "First feedback."},
        headers=get_auth_headers(student)
    )
    assert r1.status_code == 201

    # Duplicate submission
    r2 = client.post(
        "/feedback",
        json={"project_id": project.id, "rating": 3, "comment": "Second attempt."},
        headers=get_auth_headers(student)
    )
    assert r2.status_code == 400
    assert "already submitted" in r2.json()["detail"].lower()


def test_only_original_feedback_stored(client):
    """
    TC-US13-03 – After a duplicate rejection, only the original feedback remains.
    """
    db = TestingSessionLocal()
    org = create_user(db, "org5@test.com", "organization")
    student = create_user(db, "student5@test.com", "student")
    project = create_project(db, org)

    client.post(
        "/feedback",
        json={"project_id": project.id, "rating": 5, "comment": "Original."},
        headers=get_auth_headers(student)
    )
    client.post(
        "/feedback",
        json={"project_id": project.id, "rating": 1, "comment": "Override attempt."},
        headers=get_auth_headers(student)
    )

    response = client.get(f"/feedback/{project.id}", headers=get_auth_headers(student))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["rating"] == 5
    assert data[0]["comment"] == "Original."


def test_different_users_can_each_submit_feedback(client):
    """
    TC-US13-03 – Two different users may each submit one feedback for the same project.
    """
    db = TestingSessionLocal()
    org = create_user(db, "org6@test.com", "organization")
    student1 = create_user(db, "student6a@test.com", "student")
    student2 = create_user(db, "student6b@test.com", "student")
    project = create_project(db, org)

    r1 = client.post("/feedback", json={"project_id": project.id, "rating": 5}, headers=get_auth_headers(student1))
    r2 = client.post("/feedback", json={"project_id": project.id, "rating": 4}, headers=get_auth_headers(student2))

    assert r1.status_code == 201
    assert r2.status_code == 201

    response = client.get(f"/feedback/{project.id}", headers=get_auth_headers(student1))
    assert len(response.json()) == 2