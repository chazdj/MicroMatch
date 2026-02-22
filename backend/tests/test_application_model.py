import pytest
from sqlalchemy.exc import IntegrityError
from app.models import User, Project, Application
from app.schemas.user import UserRole

# ============================================================
# Helper Functions
# ============================================================

def create_student(db):
    """
    Creates and persists a student user.

    Returns:
        User: Persisted student user instance
    """
    student = User(
        email="student@test.com",
        hashed_password="hashed",
        role=UserRole.student
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def create_org(db):
    """
    Creates and persists an organization user.

    Returns:
        User: Persisted organization user instance
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
    Creates and persists a project owned by an organization.

    Args:
        db (Session): Active database session
        org (User): Organization user

    Returns:
        Project: Persisted project instance
    """
    project = Project(
        organization_id=org.id,
        title="Test Project",
        description="Test Desc"
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

# ============================================================
# Test Cases
# ============================================================

def test_application_creation(db_session):
    """
    Test that an Application:
    - Can be successfully created
    - Defaults status to 'pending'
    - Correctly links to student and project
    """
    student = create_student(db_session)
    org = create_org(db_session)
    project = create_project(db_session, org)

    application = Application(
        student_id=student.id,
        project_id=project.id
    )

    db_session.add(application)
    db_session.commit()
    db_session.refresh(application)

    assert application.status == "pending"
    assert application.student_id == student.id
    assert application.project_id == project.id


def test_unique_constraint(db_session):
    """
    Test that duplicate applications
    (same student + same project)
    are prevented at the database level.
    """
    student = create_student(db_session)
    org = create_org(db_session)
    project = create_project(db_session, org)

    app1 = Application(student_id=student.id, project_id=project.id)
    db_session.add(app1)
    db_session.commit()

    app2 = Application(student_id=student.id, project_id=project.id)
    db_session.add(app2)

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_relationship_integrity(db_session):
    """
    Test bidirectional relationships:
    - student.applications returns associated Application
    - project.applications returns associated Application
    """
    student = create_student(db_session)
    org = create_org(db_session)
    project = create_project(db_session, org)

    application = Application(
        student_id=student.id,
        project_id=project.id
    )

    db_session.add(application)
    db_session.commit()

    assert student.applications[0].id == application.id
    assert project.applications[0].id == application.id