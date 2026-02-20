import pytest
from app.models import Project, User
from app.schemas.user import UserRole


# ---------------------------------------------------------
# Helper: Create organization user
# ---------------------------------------------------------

def create_org_user(db):
    org = User(
        email="org@test.com",
        hashed_password="hashed",
        role=UserRole.organization
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


# ---------------------------------------------------------
# TC-US5-01: Retrieve Open Projects
# ---------------------------------------------------------

def test_get_open_projects(client, db_session):
    org = create_org_user(db_session)

    project1 = Project(
        organization_id=org.id,
        title="AI Research",
        description="Work on ML models",
        status="open"
    )

    project2 = Project(
        organization_id=org.id,
        title="Closed Project",
        description="Should not appear",
        status="closed"
    )

    db_session.add_all([project1, project2])
    db_session.commit()

    response = client.get("/projects")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["title"] == "AI Research"
    assert data[0]["status"] == "open"


# ---------------------------------------------------------
# TC-US5-02: Keyword Search
# ---------------------------------------------------------

def test_search_projects(client, db_session):
    org = create_org_user(db_session)

    project1 = Project(
        organization_id=org.id,
        title="AI Platform",
        description="Deep learning system",
        required_skills="python,ml",
        status="open"
    )

    project2 = Project(
        organization_id=org.id,
        title="Web Development",
        description="Frontend React project",
        required_skills="javascript,react",
        status="open"
    )

    db_session.add_all([project1, project2])
    db_session.commit()

    response = client.get("/projects?search=python")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert "python" in data[0]["required_skills"]


# ---------------------------------------------------------
# TC-US5-03: Empty Search
# ---------------------------------------------------------

def test_empty_search_returns_all_open(client, db_session):
    org = create_org_user(db_session)

    project1 = Project(
        organization_id=org.id,
        title="Data Science",
        description="Analytics project",
        status="open"
    )

    project2 = Project(
        organization_id=org.id,
        title="Backend API",
        description="FastAPI development",
        status="open"
    )

    db_session.add_all([project1, project2])
    db_session.commit()

    response = client.get("/projects?search=")

    assert response.status_code == 200
    data = response.json()

    # Should behave like no filter
    assert len(data) == 2


# ---------------------------------------------------------
# TC-US5-04: Pagination
# ---------------------------------------------------------

def test_pagination(client, db_session):
    org = create_org_user(db_session)

    # Create 5 open projects
    for i in range(5):
        project = Project(
            organization_id=org.id,
            title=f"Project {i}",
            description="Test project",
            status="open"
        )
        db_session.add(project)

    db_session.commit()

    response = client.get("/projects?skip=0&limit=2")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2