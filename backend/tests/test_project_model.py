import pytest
from app.models import Project, User

@pytest.fixture
def org_user(db_session):
    """
    Create and persist a mock organization user in the test database.

    Returns:
        User: The created organization user instance.
    """
    # Create an organization user
    user = User(email="org@example.com", hashed_password="hashed", role="organization")
    
    # Save to the database
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def project_data():
    """
    Provide sample project data for testing.

    Returns:
        dict: Valid project creation payload.
    """
    return {
        "title": "Test Project",
        "description": "A short micro-internship project",
        "required_skills": "Python,SQL",
        "duration": "2 weeks"
    }

def test_create_project_model(db_session, org_user, project_data):
    """
    Test that a Project model instance can be created and stored correctly.

    Verifies:
    - The project is saved in the database.
    - It is linked to the correct organization.
    - Fields are stored correctly.
    - Default status is set to 'open'.
    """

    # Create project linked to the organization user
    project = Project(
        organization_id=org_user.id,
        **project_data
    )

    # Persist project to the database
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    assert project.id is not None
    assert project.organization_id == org_user.id
    assert project.title == project_data["title"]
    assert project.status == "open"

    # Assertions to verify correct creation
    assert project.id is not None  # Project was successfully created
    assert project.organization_id == org_user.id  # Correct organization link
    assert project.title == project_data["title"]  # Title matches input data
    assert project.status == "open"  # Default status should be "open"
