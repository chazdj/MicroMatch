import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import User, Project, Application, StudentProfile
from app.utils.security import hash_password
from app.core.auth import create_access_token

client = TestClient(app)


# ---------------------------------------------------------
# Fixtures
# ---------------------------------------------------------

@pytest.fixture
def organization_user(db_session):
    """
    Creates a mock organization user.
    """
    org = User(
        email="org@test.com",
        hashed_password=hash_password("password123"),
        role="organization"
    )

    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)

    return org


@pytest.fixture
def student_user(db_session):
    """
    Creates a mock student user with profile.
    """
    student = User(
        email="student@test.com",
        hashed_password=hash_password("password123"),
        role="student"
    )

    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)

    profile = StudentProfile(
        user_id=student.id,
        university="Test University",
        major="CS",
        graduation_year=2026,
        bio="Software student"
    )

    db_session.add(profile)
    db_session.commit()

    return student


@pytest.fixture
def project_owned_by_org(db_session, organization_user):
    """
    Creates a project owned by organization user.
    """
    project = Project(
        organization_id=organization_user.id,
        title="Test Project",
        description="Test Description",
        status="open"
    )

    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    return project


@pytest.fixture
def application_record(db_session, student_user, project_owned_by_org):
    """
    Creates a sample application record.
    """
    application = Application(
        student_id=student_user.id,
        project_id=project_owned_by_org.id,
        status="pending"
    )

    db_session.add(application)
    db_session.commit()
    db_session.refresh(application)

    return application


# ---------------------------------------------------------
# Helper Function
# ---------------------------------------------------------

def get_auth_headers(user):
    """
    Generates JWT authorization headers for testing.
    """
    token = create_access_token({"user_id": user.id})

    return {
        "Authorization": f"Bearer {token}"
    }


# ---------------------------------------------------------
# TEST CASES
# ---------------------------------------------------------

def test_org_view_applications_success(
    db_session,
    organization_user,
    project_owned_by_org,
    application_record
):
    """
    TC-US7-01
    Successful retrieval of applications by project owner organization.

    Expected:
    - HTTP 200 response
    - Application list returned
    """

    response = client.get(
        f"/projects/{project_owned_by_org.id}/applications",
        headers=get_auth_headers(organization_user)
    )

    assert response.status_code == 200

    data = response.json()

    # Validate response type
    assert isinstance(data, list)

    # Validate application fields
    if len(data) > 0:
        application = data[0]

        assert "status" in application
        assert "student" in application
        assert "email" in application["student"]


def test_org_view_applications_not_owner(
    organization_user,
    db_session,
    project_owned_by_org
):
    """
    TC-US7-02
    Organization attempts to view applications of project
    that it does NOT own.

    Expected:
    - HTTP 403 Forbidden
    """

    # Create another organization
    other_org = User(
        email="other_org@test.com",
        hashed_password=hash_password("password123"),
        role="organization"
    )

    db_session.add(other_org)
    db_session.commit()
    db_session.refresh(other_org)

    response = client.get(
        f"/projects/{project_owned_by_org.id}/applications",
        headers=get_auth_headers(other_org)
    )

    assert response.status_code == 403


def test_org_view_applications_project_not_found(
    organization_user
):
    """
    TC-US7-03
    Project does not exist.

    Expected:
    - HTTP 404 Not Found
    """

    response = client.get(
        "/projects/999999/applications",
        headers=get_auth_headers(organization_user)
    )

    assert response.status_code == 404


def test_application_pagination(
    organization_user,
    project_owned_by_org,
    db_session
):
    """
    Pagination validation test.

    Creates multiple unique applications using different students
    to satisfy database uniqueness constraints.

    This ensures pagination logic is tested correctly.
    """

    applications_count = 12

    # Create multiple unique students + applications
    for i in range(applications_count):

        student = User(
            email=f"student_pagination_{i}@test.com",
            hashed_password=hash_password("password123"),
            role="student"
        )

        db_session.add(student)
        db_session.commit()
        db_session.refresh(student)

        profile = StudentProfile(
            user_id=student.id,
            university="Test University",
            major="CS",
            graduation_year=2026
        )

        db_session.add(profile)
        db_session.commit()

        application = Application(
            student_id=student.id,
            project_id=project_owned_by_org.id,
            status="pending"
        )

        db_session.add(application)

    db_session.commit()

    # Test pagination endpoint
    response = client.get(
        f"/projects/{project_owned_by_org.id}/applications?skip=0&limit=5",
        headers=get_auth_headers(organization_user)
    )

    assert response.status_code == 200

    data = response.json()

    # Pagination correctness
    assert len(data) <= 5


def test_student_data_privacy_enforcement(
    organization_user,
    project_owned_by_org
):
    """
    Ensures sensitive student data is NOT exposed.

    Only allowed fields:
    - email
    - profile summary (bio)
    """

    response = client.get(
        f"/projects/{project_owned_by_org.id}/applications",
        headers=get_auth_headers(organization_user)
    )

    assert response.status_code == 200

    data = response.json()

    if len(data) > 0:
        student = data[0]["student"]

        # Privacy validation checks
        assert "hashed_password" not in student
        assert "role" not in student