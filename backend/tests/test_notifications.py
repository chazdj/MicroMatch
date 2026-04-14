import pytest
from app.models import User, Project, Application, Deliverable, Notification
from app.utils.security import hash_password
from app.core.auth import create_access_token
from tests.conftest import TestingSessionLocal


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

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


def create_project(db, org, title="Test Project"):
    project = Project(
        organization_id=org.id,
        title=title,
        description="Test description",
        status="open"
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def create_application(db, student, project, status="pending"):
    app = Application(
        student_id=student.id,
        project_id=project.id,
        status=status
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    return app


def create_deliverable(db, application, status="submitted"):
    d = Deliverable(
        application_id=application.id,
        content="My deliverable content",
        status=status
    )
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


# ---------------------------------------------------------
# TC-US16-01: Notification created on application acceptance
# ---------------------------------------------------------

def test_notification_created_on_acceptance(client):
    """
    When an organization accepts a student's application,
    the student receives a notification with is_read=False.
    """
    db = TestingSessionLocal()

    org = create_user(db, "org_accept@test.com", "organization")
    student = create_user(db, "student_accept@test.com", "student")
    project = create_project(db, org, title="Accepted Project")
    application = create_application(db, student, project)

    response = client.patch(
        f"/applications/{application.id}/status",
        json={"status": "accepted"},
        headers=get_auth_headers(org)
    )

    assert response.status_code == 200

    notification = db.query(Notification).filter(
        Notification.recipient_id == student.id
    ).first()

    assert notification is not None
    assert notification.recipient_id == student.id
    assert notification.is_read is False
    assert "accepted" in notification.message.lower()
    assert notification.created_at is not None


# ---------------------------------------------------------
# TC-US16-02: Notification created on application rejection
# ---------------------------------------------------------

def test_notification_created_on_rejection(client):
    """
    When an organization rejects a student's application,
    the student receives a notification with is_read=False.
    """
    db = TestingSessionLocal()

    org = create_user(db, "org_reject@test.com", "organization")
    student = create_user(db, "student_reject@test.com", "student")
    project = create_project(db, org, title="Rejected Project")
    application = create_application(db, student, project)

    response = client.patch(
        f"/applications/{application.id}/status",
        json={"status": "rejected"},
        headers=get_auth_headers(org)
    )

    assert response.status_code == 200

    notification = db.query(Notification).filter(
        Notification.recipient_id == student.id
    ).first()

    assert notification is not None
    assert notification.recipient_id == student.id
    assert notification.is_read is False
    assert "rejected" in notification.message.lower()
    assert notification.created_at is not None


# ---------------------------------------------------------
# TC-US16-03: Notification created on deliverable review
# ---------------------------------------------------------

def test_notification_created_on_deliverable_review(client):
    """
    When an organization reviews a deliverable,
    the submitting student receives a notification.
    """
    db = TestingSessionLocal()

    org = create_user(db, "org_review@test.com", "organization")
    student = create_user(db, "student_review@test.com", "student")
    project = create_project(db, org, title="Review Project")
    application = create_application(db, student, project, status="accepted")
    deliverable = create_deliverable(db, application)

    response = client.put(
        f"/deliverables/{deliverable.id}/review",
        json={"status": "accepted"},
        headers=get_auth_headers(org)
    )

    assert response.status_code == 200

    notification = db.query(Notification).filter(
        Notification.recipient_id == student.id
    ).first()

    assert notification is not None
    assert notification.recipient_id == student.id
    assert notification.is_read is False
    assert "accepted" in notification.message.lower()
    assert notification.created_at is not None


# ---------------------------------------------------------
# TC-US16-04: Notification created on project completion
# ---------------------------------------------------------

def test_notification_created_on_project_completion(client):
    """
    When a project is marked complete, the accepted student
    receives a completion notification with is_read=False.
    """
    db = TestingSessionLocal()

    org = create_user(db, "org_complete@test.com", "organization")
    student = create_user(db, "student_complete@test.com", "student")
    project = create_project(db, org, title="Completed Project")
    application = create_application(db, student, project, status="accepted")
    deliverable = create_deliverable(db, application, status="accepted")

    response = client.put(
        f"/projects/{project.id}/complete",
        headers=get_auth_headers(org)
    )

    assert response.status_code == 200

    notification = db.query(Notification).filter(
        Notification.recipient_id == student.id
    ).first()

    assert notification is not None
    assert notification.recipient_id == student.id
    assert notification.is_read is False
    assert "complete" in notification.message.lower()
    assert notification.created_at is not None


# ---------------------------------------------------------
# TC-US16-05: Correct student receives notification, not another
# ---------------------------------------------------------

def test_notification_only_sent_to_correct_student(client):
    """
    Only the student whose application was acted on
    receives the notification — not other students.
    """
    db = TestingSessionLocal()

    org = create_user(db, "org_targeted@test.com", "organization")
    student1 = create_user(db, "student_targeted1@test.com", "student")
    student2 = create_user(db, "student_targeted2@test.com", "student")
    project = create_project(db, org, title="Targeted Notification Project")

    app1 = create_application(db, student1, project)
    create_application(db, student2, project)

    client.patch(
        f"/applications/{app1.id}/status",
        json={"status": "accepted"},
        headers=get_auth_headers(org)
    )

    # student1 should have a notification
    s1_notification = db.query(Notification).filter(
        Notification.recipient_id == student1.id
    ).first()
    assert s1_notification is not None

    # student2 should NOT have a notification from this event
    # (auto-reject fires but does not generate a notification — by design)
    s2_notification = db.query(Notification).filter(
        Notification.recipient_id == student2.id
    ).first()
    assert s2_notification is None


# ---------------------------------------------------------
# TC-US16-06: Notification defaults to unread
# ---------------------------------------------------------

def test_notification_defaults_to_unread(client):
    """
    All newly created notifications must have is_read=False.
    """
    db = TestingSessionLocal()

    org = create_user(db, "org_unread@test.com", "organization")
    student = create_user(db, "student_unread@test.com", "student")
    project = create_project(db, org)
    application = create_application(db, student, project)

    client.patch(
        f"/applications/{application.id}/status",
        json={"status": "accepted"},
        headers=get_auth_headers(org)
    )

    notification = db.query(Notification).filter(
        Notification.recipient_id == student.id
    ).first()

    assert notification.is_read is False