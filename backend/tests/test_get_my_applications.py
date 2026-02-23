from app.models import User, Project, Application
from app.schemas.user import UserRole
from app.core.dependencies import get_current_user
from app.main import app


# ---------------------------------------------------------
# Helper: Authentication Override
# ---------------------------------------------------------

def override_auth_dependency(user):
    """
    Overrides authentication dependency to inject a user.

    Bypasses JWT validation layer for clean endpoint testing.
    """
    app.dependency_overrides[get_current_user] = lambda: user


# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------

def create_student(db, email="student@test.com"):
    """
    Creates and returns a student user.
    """
    student = User(
        email=email,
        hashed_password="hashed",
        role=UserRole.student
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def create_org(db):
    """
    Creates and returns an organization user.
    """
    org = User(
        email="org@test.com",
        hashed_password="hashed",
        role=UserRole.organization
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


def create_project(db, org):
    """
    Creates and returns a project owned by the organization.
    """
    project = Project(
        organization_id=org.id,
        title="Test Project",
        description="Test Description"
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def create_application(db, student, project):
    """
    Creates and returns an application for a student.
    """
    application = Application(
        student_id=student.id,
        project_id=project.id
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


# ---------------------------------------------------------
# Test Cases
# ---------------------------------------------------------

def test_student_can_view_own_applications(client, db_session):
    """
    Ensures a student can retrieve their own applications.
    """

    student = create_student(db_session)
    org = create_org(db_session)
    project = create_project(db_session, org)
    create_application(db_session, student, project)

    override_auth_dependency(student)

    response = client.get("/applications/me")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["student_id"] == student.id
    assert data[0]["project_id"] == project.id
    assert data[0]["status"] == "pending"


def test_returns_empty_list_when_no_applications(client, db_session):
    """
    Ensures endpoint returns empty list if student has no applications.
    """

    student = create_student(db_session)

    override_auth_dependency(student)

    response = client.get("/applications/me")

    assert response.status_code == 200
    assert response.json() == []


def test_student_cannot_see_other_students_applications(client, db_session):
    """
    Ensures a student only sees their own applications.
    """

    student1 = create_student(db_session, email="student1@test.com")
    student2 = create_student(db_session, email="student2@test.com")

    org = create_org(db_session)
    project = create_project(db_session, org)

    create_application(db_session, student1, project)

    override_auth_dependency(student2)

    response = client.get("/applications/me")

    assert response.status_code == 200
    assert response.json() == []


def test_only_students_can_access_endpoint(client, db_session):
    """
    Ensures non-student users cannot access this endpoint.
    """

    org = create_org(db_session)

    override_auth_dependency(org)

    response = client.get("/applications/me")

    # require_role("student") should reject this
    assert response.status_code == 403