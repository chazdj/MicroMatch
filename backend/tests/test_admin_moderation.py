from app.models import User, Project
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


# ----------------------------
# TC-US14-01: Admin Views All Projects
# ----------------------------

def test_admin_can_view_all_projects(client):
    """
    TC-US14-01 – Admin retrieves all projects regardless of status.
    Expected: HTTP 200, all projects returned.
    """
    db = TestingSessionLocal()
    admin = create_user(db, "admin@test.com", "admin")
    org = create_user(db, "org@test.com", "organization")
    create_project(db, org, status="open")
    create_project(db, org, status="completed")
    create_project(db, org, status="disabled")

    response = client.get("/admin/projects", headers=get_auth_headers(admin))

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_admin_projects_response_schema(client):
    """
    TC-US14-01 – Validates each project in response has expected fields.
    """
    db = TestingSessionLocal()
    admin = create_user(db, "admin_schema@test.com", "admin")
    org = create_user(db, "org_schema@test.com", "organization")
    create_project(db, org)

    response = client.get("/admin/projects", headers=get_auth_headers(admin))

    assert response.status_code == 200
    project = response.json()[0]
    assert "id" in project
    assert "title" in project
    assert "status" in project
    assert "organization_id" in project


def test_admin_sees_projects_of_all_statuses(client):
    """
    TC-US14-01 – Admin endpoint returns projects in all statuses including disabled.
    """
    db = TestingSessionLocal()
    admin = create_user(db, "admin_all@test.com", "admin")
    org = create_user(db, "org_all@test.com", "organization")
    create_project(db, org, status="open")
    create_project(db, org, status="in_progress")
    create_project(db, org, status="completed")
    create_project(db, org, status="disabled")

    response = client.get("/admin/projects", headers=get_auth_headers(admin))

    statuses = {p["status"] for p in response.json()}
    assert "open" in statuses
    assert "disabled" in statuses
    assert "completed" in statuses


# ----------------------------
# TC-US14-02: Admin Removes Project
# ----------------------------

def test_admin_can_disable_project(client):
    """
    TC-US14-02 – Admin disables a project by setting status to 'disabled'.
    Expected: HTTP 200, project status = 'disabled'.
    """
    db = TestingSessionLocal()
    admin = create_user(db, "admin2@test.com", "admin")
    org = create_user(db, "org2@test.com", "organization")
    project = create_project(db, org, status="open")

    response = client.delete(
        f"/admin/listings/{project.id}",
        headers=get_auth_headers(admin)
    )

    assert response.status_code == 200
    db.refresh(project)
    assert project.status == "disabled"


def test_disabled_project_not_visible_to_students(client):
    """
    TC-US14-02 – After disabling, project no longer appears in open project listings.
    """
    db = TestingSessionLocal()
    admin = create_user(db, "admin3@test.com", "admin")
    org = create_user(db, "org3@test.com", "organization")
    project = create_project(db, org, status="open")

    # Disable it
    client.delete(f"/admin/listings/{project.id}", headers=get_auth_headers(admin))

    # Check public listing
    response = client.get("/projects")
    ids = [p["id"] for p in response.json()]
    assert project.id not in ids


def test_admin_disable_project_not_found(client):
    """
    TC-US14-02 – Attempting to disable a non-existent project.
    Expected: HTTP 404.
    """
    db = TestingSessionLocal()
    admin = create_user(db, "admin4@test.com", "admin")

    response = client.delete("/admin/listings/999999", headers=get_auth_headers(admin))

    assert response.status_code == 404


def test_admin_can_suspend_user(client):
    """
    TC-US14-02 – Admin sets a user's is_active to False (suspend).
    Expected: HTTP 200, user is_active = False.
    """
    db = TestingSessionLocal()
    admin = create_user(db, "admin5@test.com", "admin")
    target = create_user(db, "target@test.com", "student")

    response = client.put(
        f"/admin/users/{target.id}/status?is_active=false",
        headers=get_auth_headers(admin)
    )

    assert response.status_code == 200
    db.refresh(target)
    assert target.is_active is False


def test_admin_can_reactivate_user(client):
    """
    TC-US14-02 – Admin reactivates a previously suspended user.
    """
    db = TestingSessionLocal()
    admin = create_user(db, "admin6@test.com", "admin")
    target = create_user(db, "target2@test.com", "student")
    target.is_active = False
    db.commit()

    response = client.put(
        f"/admin/users/{target.id}/status?is_active=true",
        headers=get_auth_headers(admin)
    )

    assert response.status_code == 200
    db.refresh(target)
    assert target.is_active is True


# ----------------------------
# TC-US14-03: Unauthorized Access Blocked
# ----------------------------

def test_student_cannot_access_admin_projects(client):
    """
    TC-US14-03 – Student cannot access admin project listing.
    Expected: HTTP 403.
    """
    db = TestingSessionLocal()
    student = create_user(db, "student_unauth@test.com", "student")

    response = client.get("/admin/projects", headers=get_auth_headers(student))

    assert response.status_code == 403


def test_org_cannot_access_admin_projects(client):
    """
    TC-US14-03 – Organization cannot access admin project listing.
    Expected: HTTP 403.
    """
    db = TestingSessionLocal()
    org = create_user(db, "org_unauth@test.com", "organization")

    response = client.get("/admin/projects", headers=get_auth_headers(org))

    assert response.status_code == 403


def test_student_cannot_disable_project(client):
    """
    TC-US14-03 – Student cannot call the disable project endpoint.
    Expected: HTTP 403.
    """
    db = TestingSessionLocal()
    org = create_user(db, "org_owner@test.com", "organization")
    student = create_user(db, "student_disable@test.com", "student")
    project = create_project(db, org)

    response = client.delete(
        f"/admin/listings/{project.id}",
        headers=get_auth_headers(student)
    )

    assert response.status_code == 403


def test_unauthenticated_cannot_access_admin(client):
    """
    TC-US14-03 – Unauthenticated request to admin endpoint is rejected.
    Expected: HTTP 401.
    """
    response = client.get("/admin/projects")

    assert response.status_code == 401


def test_student_cannot_suspend_user(client):
    """
    TC-US14-03 – Student cannot modify another user's active status.
    Expected: HTTP 403.
    """
    db = TestingSessionLocal()
    student = create_user(db, "student_suspend@test.com", "student")
    target = create_user(db, "target_suspend@test.com", "student")

    response = client.put(
        f"/admin/users/{target.id}/status?is_active=false",
        headers=get_auth_headers(student)
    )

    assert response.status_code == 403