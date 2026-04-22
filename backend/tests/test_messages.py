import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import User, Project, Application
from app.schemas.user import UserRole
from app.utils.security import hash_password


# ---------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------

def create_user(db, email, role):
    user = User(
        email=email,
        hashed_password=hash_password("password123"),
        role=role,
        name="Test User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login(client, email):
    resp = client.post("/auth/login", json={"email": email, "password": "password123"})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def create_project(db, org_id):
    project = Project(
        organization_id=org_id,
        title="Test Project",
        description="A test project",
        required_skills="Python",
        duration="2 weeks",
        status="open"
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def accept_student(db, student_id, project_id):
    app_obj = Application(
        student_id=student_id,
        project_id=project_id,
        status="accepted"
    )
    db.add(app_obj)
    db.commit()
    db.refresh(app_obj)
    return app_obj


# ---------------------------------------------------------------
# Unit Tests — POST /projects/{id}/messages
# ---------------------------------------------------------------

class TestSendMessage:

    def test_org_can_send_message(self, client, db_session):
        """Organization that owns the project can send a message."""
        org = create_user(db_session, "org@test.com", UserRole.organization)
        student = create_user(db_session, "student@test.com", UserRole.student)
        project = create_project(db_session, org.id)
        accept_student(db_session, student.id, project.id)

        token = login(client, "org@test.com")
        resp = client.post(
            f"/projects/{project.id}/messages",
            json={"content": "Hello student!"},
            headers=auth_header(token)
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["content"] == "Hello student!"
        assert data["sender_id"] == org.id
        assert data["project_id"] == project.id

    def test_accepted_student_can_send_message(self, client, db_session):
        """Accepted student can send a message in their project."""
        org = create_user(db_session, "org@test.com", UserRole.organization)
        student = create_user(db_session, "student@test.com", UserRole.student)
        project = create_project(db_session, org.id)
        accept_student(db_session, student.id, project.id)

        token = login(client, "student@test.com")
        resp = client.post(
            f"/projects/{project.id}/messages",
            json={"content": "Hi! I have a question."},
            headers=auth_header(token)
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["content"] == "Hi! I have a question."
        assert data["sender_id"] == student.id

    def test_unassigned_student_blocked(self, client, db_session):
        """Student with no accepted application cannot send messages."""
        org = create_user(db_session, "org@test.com", UserRole.organization)
        create_user(db_session, "outsider@test.com", UserRole.student)
        project = create_project(db_session, org.id)

        token = login(client, "outsider@test.com")
        resp = client.post(
            f"/projects/{project.id}/messages",
            json={"content": "Let me in!"},
            headers=auth_header(token)
        )
        assert resp.status_code == 403

    def test_wrong_org_blocked(self, client, db_session):
        """Organization that does NOT own the project is blocked."""
        org1 = create_user(db_session, "org1@test.com", UserRole.organization)
        create_user(db_session, "org2@test.com", UserRole.organization)
        project = create_project(db_session, org1.id)

        token = login(client, "org2@test.com")
        resp = client.post(
            f"/projects/{project.id}/messages",
            json={"content": "Sneaky message"},
            headers=auth_header(token)
        )
        assert resp.status_code == 403

    def test_unauthenticated_blocked(self, client, db_session):
        """Unauthenticated request is rejected."""
        org = create_user(db_session, "org@test.com", UserRole.organization)
        project = create_project(db_session, org.id)

        resp = client.post(
            f"/projects/{project.id}/messages",
            json={"content": "No token"}
        )
        assert resp.status_code == 401

    def test_nonexistent_project_returns_404(self, client, db_session):
        """Messaging a non-existent project returns 404."""
        create_user(db_session, "org@test.com", UserRole.organization)
        token = login(client, "org@test.com")

        resp = client.post(
            "/projects/99999/messages",
            json={"content": "Ghost project"},
            headers=auth_header(token)
        )
        assert resp.status_code == 404

    def test_pending_student_blocked(self, client, db_session):
        """Student with only a pending application is blocked."""
        org = create_user(db_session, "org@test.com", UserRole.organization)
        student = create_user(db_session, "student@test.com", UserRole.student)
        project = create_project(db_session, org.id)

        # Pending, not accepted
        app_obj = Application(
            student_id=student.id,
            project_id=project.id,
            status="pending"
        )
        db_session.add(app_obj)
        db_session.commit()

        token = login(client, "student@test.com")
        resp = client.post(
            f"/projects/{project.id}/messages",
            json={"content": "Am I in?"},
            headers=auth_header(token)
        )
        assert resp.status_code == 403


# ---------------------------------------------------------------
# Unit Tests — GET /projects/{id}/messages
# ---------------------------------------------------------------

class TestGetMessages:

    def test_returns_ordered_conversation(self, client, db_session):
        """Messages are returned oldest → newest."""
        org = create_user(db_session, "org@test.com", UserRole.organization)
        student = create_user(db_session, "student@test.com", UserRole.student)
        project = create_project(db_session, org.id)
        accept_student(db_session, student.id, project.id)

        org_token = login(client, "org@test.com")
        student_token = login(client, "student@test.com")

        client.post(f"/projects/{project.id}/messages", json={"content": "First"}, headers=auth_header(org_token))
        client.post(f"/projects/{project.id}/messages", json={"content": "Second"}, headers=auth_header(student_token))
        client.post(f"/projects/{project.id}/messages", json={"content": "Third"}, headers=auth_header(org_token))

        resp = client.get(f"/projects/{project.id}/messages", headers=auth_header(org_token))
        assert resp.status_code == 200
        messages = resp.json()
        assert len(messages) == 3
        assert messages[0]["content"] == "First"
        assert messages[1]["content"] == "Second"
        assert messages[2]["content"] == "Third"

    def test_empty_history_returns_empty_list(self, client, db_session):
        """No messages yet returns an empty list."""
        org = create_user(db_session, "org@test.com", UserRole.organization)
        project = create_project(db_session, org.id)

        token = login(client, "org@test.com")
        resp = client.get(f"/projects/{project.id}/messages", headers=auth_header(token))
        assert resp.status_code == 200
        assert resp.json() == []

    def test_unauthorized_user_cannot_read(self, client, db_session):
        """User outside the project cannot read messages."""
        org = create_user(db_session, "org@test.com", UserRole.organization)
        create_user(db_session, "outsider@test.com", UserRole.student)
        project = create_project(db_session, org.id)

        token = login(client, "outsider@test.com")
        resp = client.get(f"/projects/{project.id}/messages", headers=auth_header(token))
        assert resp.status_code == 403

    def test_messages_contain_sender_info(self, client, db_session):
        """Message responses include sender email and role."""
        org = create_user(db_session, "org@test.com", UserRole.organization)
        project = create_project(db_session, org.id)
        token = login(client, "org@test.com")

        client.post(f"/projects/{project.id}/messages", json={"content": "Hey!"}, headers=auth_header(token))
        resp = client.get(f"/projects/{project.id}/messages", headers=auth_header(token))
        assert resp.status_code == 200
        msg = resp.json()[0]
        assert "sender" in msg
        assert msg["sender"]["email"] == "org@test.com"


# ---------------------------------------------------------------
# E2E Test — Full conversation workflow
# ---------------------------------------------------------------

class TestMessagingE2E:

    def test_full_conversation_workflow(self, client, db_session):
        """
        E2E: org creates project → student applies + gets accepted →
        student messages org → org replies → history persists in order.
        """
        # 1. Register and login org
        org = create_user(db_session, "org@company.com", UserRole.organization)
        student = create_user(db_session, "student@uni.edu", UserRole.student)
        org_token = login(client, "org@company.com")
        student_token = login(client, "student@uni.edu")

        # 2. Org creates project
        project = create_project(db_session, org.id)

        # 3. Student applies and gets accepted
        accept_student(db_session, student.id, project.id)

        # 4. Student sends first message
        r1 = client.post(
            f"/projects/{project.id}/messages",
            json={"content": "Hi! When does work start?"},
            headers=auth_header(student_token)
        )
        assert r1.status_code == 201

        # 5. Org replies
        r2 = client.post(
            f"/projects/{project.id}/messages",
            json={"content": "Next Monday, welcome aboard!"},
            headers=auth_header(org_token)
        )
        assert r2.status_code == 201

        # 6. Student replies again
        r3 = client.post(
            f"/projects/{project.id}/messages",
            json={"content": "Perfect, thank you!"},
            headers=auth_header(student_token)
        )
        assert r3.status_code == 201

        # 7. Fetch conversation history as org
        history = client.get(
            f"/projects/{project.id}/messages",
            headers=auth_header(org_token)
        ).json()

        assert len(history) == 3
        assert history[0]["content"] == "Hi! When does work start?"
        assert history[0]["sender"]["email"] == "student@uni.edu"
        assert history[1]["content"] == "Next Monday, welcome aboard!"
        assert history[1]["sender"]["email"] == "org@company.com"
        assert history[2]["content"] == "Perfect, thank you!"

        # 8. Verify an outsider still cannot read
        outsider = create_user(db_session, "hacker@evil.com", UserRole.student)
        outsider_token = login(client, "hacker@evil.com")
        blocked = client.get(
            f"/projects/{project.id}/messages",
            headers=auth_header(outsider_token)
        )
        assert blocked.status_code == 403