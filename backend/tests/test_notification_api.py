from app.models import User, Project, Application, Notification
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


def seed_notification(db, recipient, message="Test notification", is_read=False):
    """
    Directly inserts a notification record — used to set up test state
    without going through the event hook.
    """
    n = Notification(
        recipient_id=recipient.id,
        message=message,
        is_read=is_read
    )
    db.add(n)
    db.commit()
    db.refresh(n)
    return n


# ---------------------------------------------------------
# GET /notifications
# ---------------------------------------------------------

def test_get_notifications_returns_own_only(client):
    """
    TC-US16-05: User only sees their own notifications.
    """
    db = TestingSessionLocal()

    student1 = create_user(db, "s1@test.com", "student")
    student2 = create_user(db, "s2@test.com", "student")

    seed_notification(db, student1, "Notification for student1")
    seed_notification(db, student2, "Notification for student2")

    response = client.get("/notifications", headers=get_auth_headers(student1))

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["recipient_id"] == student1.id
    assert data[0]["message"] == "Notification for student1"


def test_get_notifications_empty_list(client):
    """
    User with no notifications receives empty list — not a 404.
    """
    db = TestingSessionLocal()

    student = create_user(db, "empty@test.com", "student")

    response = client.get("/notifications", headers=get_auth_headers(student))

    assert response.status_code == 200
    assert response.json() == []


def test_get_notifications_newest_first(client):
    """
    Results are ordered newest-first (descending by id).
    SQLite has second-level timestamp precision so we sort by id
    as a reliable tiebreaker for same-second inserts.
    """
    db = TestingSessionLocal()

    student = create_user(db, "ordered@test.com", "student")

    n1 = seed_notification(db, student, "First notification")
    n2 = seed_notification(db, student, "Second notification")
    n3 = seed_notification(db, student, "Third notification")

    response = client.get("/notifications", headers=get_auth_headers(student))

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 3

    # Highest id (most recently inserted) should appear first
    returned_ids = [item["id"] for item in data]
    assert returned_ids == [n3.id, n2.id, n1.id]

def test_get_notifications_requires_auth(client):
    """
    TC-US16-07: Unauthenticated request returns 401.
    """
    response = client.get("/notifications")
    assert response.status_code == 401


def test_get_notifications_response_schema(client):
    """
    Response objects contain all required fields.
    """
    db = TestingSessionLocal()

    student = create_user(db, "schema@test.com", "student")
    seed_notification(db, student, "Schema test")

    response = client.get("/notifications", headers=get_auth_headers(student))

    assert response.status_code == 200
    item = response.json()[0]

    assert "id" in item
    assert "recipient_id" in item
    assert "message" in item
    assert "is_read" in item
    assert "created_at" in item
    assert item["is_read"] is False


# ---------------------------------------------------------
# PUT /notifications/{id}/read
# ---------------------------------------------------------

def test_mark_notification_read_success(client):
    """
    TC-US16-06: Authenticated user can mark their own notification as read.
    """
    db = TestingSessionLocal()

    student = create_user(db, "markread@test.com", "student")
    notification = seed_notification(db, student, "Mark me read")

    assert notification.is_read is False

    response = client.put(
        f"/notifications/{notification.id}/read",
        headers=get_auth_headers(student)
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_read"] is True
    assert data["id"] == notification.id


def test_mark_notification_read_persists(client):
    """
    is_read=True persists in the database after the update.
    """
    db = TestingSessionLocal()

    student = create_user(db, "persist@test.com", "student")
    notification = seed_notification(db, student, "Persist test")

    client.put(
        f"/notifications/{notification.id}/read",
        headers=get_auth_headers(student)
    )

    db.refresh(notification)
    assert notification.is_read is True


def test_mark_notification_read_idempotent(client):
    """
    Marking an already-read notification as read again returns 200 — no error.
    """
    db = TestingSessionLocal()

    student = create_user(db, "idempotent@test.com", "student")
    notification = seed_notification(db, student, "Already read", is_read=True)

    response = client.put(
        f"/notifications/{notification.id}/read",
        headers=get_auth_headers(student)
    )

    assert response.status_code == 200
    assert response.json()["is_read"] is True


def test_mark_other_users_notification_forbidden(client):
    """
    TC-US16-07: User cannot mark another user's notification as read — returns 403.
    """
    db = TestingSessionLocal()

    student1 = create_user(db, "owner_notif@test.com", "student")
    student2 = create_user(db, "intruder_notif@test.com", "student")

    notification = seed_notification(db, student1, "Belongs to student1")

    response = client.put(
        f"/notifications/{notification.id}/read",
        headers=get_auth_headers(student2)
    )

    assert response.status_code == 403


def test_mark_notification_read_not_found(client):
    """
    Attempting to mark a non-existent notification returns 404.
    """
    db = TestingSessionLocal()

    student = create_user(db, "notfound@test.com", "student")

    response = client.put(
        "/notifications/999999/read",
        headers=get_auth_headers(student)
    )

    assert response.status_code == 404


def test_mark_notification_read_requires_auth(client):
    """
    TC-US16-07: Unauthenticated request to mark-read returns 401.
    """
    response = client.put("/notifications/1/read")
    assert response.status_code == 401


def test_org_user_can_receive_and_read_notifications(client):
    """
    Organization users can also receive and read notifications
    since get_current_user is role-agnostic.
    """
    db = TestingSessionLocal()

    org = create_user(db, "org_notif@test.com", "organization")
    notification = seed_notification(db, org, "Org notification")

    # GET
    get_response = client.get("/notifications", headers=get_auth_headers(org))
    assert get_response.status_code == 200
    assert len(get_response.json()) == 1

    # PUT read
    put_response = client.put(
        f"/notifications/{notification.id}/read",
        headers=get_auth_headers(org)
    )
    assert put_response.status_code == 200
    assert put_response.json()["is_read"] is True