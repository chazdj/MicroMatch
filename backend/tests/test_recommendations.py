"""
test_recommendations.py
=======================
Endpoint tests for GET /recommendations (Issue #90).

Covers:
- Auth: student only, org denied, unauthenticated denied
- No profile → 404
- No open projects → empty list
- Returns ranked results descending
- score + rank fields present
- Inactive/closed projects excluded
- top_n query param slicing
- Determinism: same request → same order
"""

from app.models import (
    User, StudentProfile, Project,
    Application, Deliverable, Feedback
)
from app.utils.security import hash_password
from app.core.auth import create_access_token
from tests.conftest import TestingSessionLocal


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_auth_headers(user):
    token = create_access_token({"user_id": user.id})
    return {"Authorization": f"Bearer {token}"}


def create_student(db, email="student@test.com"):
    user = User(
        email=email,
        hashed_password=hash_password("password"),
        role="student"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_org(db, email="org@test.com"):
    user = User(
        email=email,
        hashed_password=hash_password("password"),
        role="organization"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_profile(db, student, skills="python,fastapi,sql"):
    profile = StudentProfile(
        user_id=student.id,
        university="Test University",
        major="Computer Science",
        graduation_year=2025,
        skills=skills,
        bio="I enjoy backend development with Python and APIs",
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def create_project(db, org, title="Test Project", required_skills="python,sql",
                   status="open", description="A Python and SQL backend project"):
    project = Project(
        organization_id=org.id,
        title=title,
        description=description,
        required_skills=required_skills,
        duration="1 month",
        status=status,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


# ---------------------------------------------------------------------------
# Auth tests
# ---------------------------------------------------------------------------

def test_recommendations_requires_auth(client):
    """Unauthenticated request returns 401."""
    response = client.get("/recommendations")
    assert response.status_code == 401


def test_recommendations_org_denied(client):
    """Organization user cannot access recommendations — returns 403."""
    db = TestingSessionLocal()
    org = create_org(db, "org_denied@test.com")

    response = client.get("/recommendations", headers=get_auth_headers(org))
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# Profile guard
# ---------------------------------------------------------------------------

def test_recommendations_no_profile_returns_404(client):
    """Student without a profile gets 404."""
    db = TestingSessionLocal()
    student = create_student(db, "noprofile@test.com")

    response = client.get("/recommendations", headers=get_auth_headers(student))
    assert response.status_code == 404
    assert "profile" in response.json()["detail"].lower()


# ---------------------------------------------------------------------------
# Empty / no open projects
# ---------------------------------------------------------------------------

def test_recommendations_no_open_projects_returns_empty_list(client):
    """No open projects → empty list, not an error."""
    db = TestingSessionLocal()
    student = create_student(db, "empty@test.com")
    org = create_org(db, "empty_org@test.com")
    create_profile(db, student)

    # All projects are closed or completed — none open
    create_project(db, org, title="Closed", status="closed")
    create_project(db, org, title="Completed", status="completed")

    response = client.get("/recommendations", headers=get_auth_headers(student))
    assert response.status_code == 200
    assert response.json() == []


# ---------------------------------------------------------------------------
# Response structure
# ---------------------------------------------------------------------------

def test_recommendations_response_schema(client):
    """Response items contain all required fields."""
    db = TestingSessionLocal()
    student = create_student(db, "schema@test.com")
    org = create_org(db, "schema_org@test.com")
    create_profile(db, student)
    create_project(db, org, title="Schema Project")

    response = client.get("/recommendations", headers=get_auth_headers(student))
    assert response.status_code == 200

    data = response.json()
    assert len(data) >= 1

    item = data[0]
    assert "project_id" in item
    assert "title" in item
    assert "match_score" in item
    assert "rank" in item
    assert "skill_score" in item
    assert "experience_score" in item
    assert "interest_score" in item
    assert "activity_score" in item
    assert "success_score" in item


def test_recommendations_scores_in_range(client):
    """All scores must be between 0 and 100."""
    db = TestingSessionLocal()
    student = create_student(db, "range@test.com")
    org = create_org(db, "range_org@test.com")
    create_profile(db, student)
    create_project(db, org, title="Range Project")

    response = client.get("/recommendations", headers=get_auth_headers(student))
    assert response.status_code == 200

    for item in response.json():
        assert 0.0 <= item["match_score"] <= 100.0
        assert 0.0 <= item["skill_score"] <= 100.0
        assert 0.0 <= item["success_score"] <= 100.0


# ---------------------------------------------------------------------------
# Ranking correctness
# ---------------------------------------------------------------------------

def test_recommendations_sorted_descending(client):
    """Results must be sorted by match_score descending."""
    db = TestingSessionLocal()
    student = create_student(db, "sorted@test.com")
    org = create_org(db, "sorted_org@test.com")
    create_profile(db, student, skills="python,fastapi,sql")

    # High match — all skills align
    create_project(db, org, title="High Match",
                   required_skills="python,fastapi,sql",
                   description="Python FastAPI SQL backend project")
    # Low match — no skill overlap
    create_project(db, org, title="Low Match",
                   required_skills="photoshop,illustrator,figma",
                   description="Graphic design and UI work")

    response = client.get("/recommendations", headers=get_auth_headers(student))
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    assert data[0]["match_score"] >= data[1]["match_score"]


def test_recommendations_rank_field_correct(client):
    """Rank 1 should have the highest score."""
    db = TestingSessionLocal()
    student = create_student(db, "rank@test.com")
    org = create_org(db, "rank_org@test.com")
    create_profile(db, student, skills="python,sql")

    create_project(db, org, title="A", required_skills="python,sql")
    create_project(db, org, title="B", required_skills="java,kotlin")

    response = client.get("/recommendations", headers=get_auth_headers(student))
    assert response.status_code == 200

    data = response.json()
    ranks = [item["rank"] for item in data]
    assert ranks[0] == 1
    assert ranks == list(range(1, len(data) + 1))


def test_recommendations_best_skill_match_ranks_first(client):
    """Project with full skill overlap must rank above one with none."""
    db = TestingSessionLocal()
    student = create_student(db, "skillrank@test.com")
    org = create_org(db, "skillrank_org@test.com")
    create_profile(db, student, skills="python,fastapi")

    perfect = create_project(db, org, title="Perfect",
                              required_skills="python,fastapi",
                              description="Python FastAPI project")
    no_match = create_project(db, org, title="No Match",
                               required_skills="verilog,fpga",
                               description="Hardware embedded project")

    response = client.get("/recommendations", headers=get_auth_headers(student))
    assert response.status_code == 200

    data = response.json()
    top = data[0]
    assert top["project_id"] == perfect.id


# ---------------------------------------------------------------------------
# Inactive projects excluded
# ---------------------------------------------------------------------------

def test_recommendations_excludes_closed_projects(client):
    """Closed projects must not appear in results."""
    db = TestingSessionLocal()
    student = create_student(db, "closed@test.com")
    org = create_org(db, "closed_org@test.com")
    create_profile(db, student)

    open_p = create_project(db, org, title="Open Project", status="open")
    closed_p = create_project(db, org, title="Closed Project", status="closed")

    response = client.get("/recommendations", headers=get_auth_headers(student))
    assert response.status_code == 200

    returned_ids = [item["project_id"] for item in response.json()]
    assert open_p.id in returned_ids
    assert closed_p.id not in returned_ids


def test_recommendations_excludes_completed_projects(client):
    """Completed projects must not appear in results."""
    db = TestingSessionLocal()
    student = create_student(db, "completed@test.com")
    org = create_org(db, "completed_org@test.com")
    create_profile(db, student)

    open_p = create_project(db, org, title="Open Project", status="open")
    done_p = create_project(db, org, title="Done Project", status="completed")

    response = client.get("/recommendations", headers=get_auth_headers(student))
    assert response.status_code == 200

    returned_ids = [item["project_id"] for item in response.json()]
    assert open_p.id in returned_ids
    assert done_p.id not in returned_ids


# ---------------------------------------------------------------------------
# top_n query param
# ---------------------------------------------------------------------------

def test_recommendations_top_n_slices_results(client):
    """top_n=1 returns only the single best match."""
    db = TestingSessionLocal()
    student = create_student(db, "topn@test.com")
    org = create_org(db, "topn_org@test.com")
    create_profile(db, student)

    for i in range(5):
        create_project(db, org, title=f"Project {i}", status="open")

    response = client.get("/recommendations?top_n=1", headers=get_auth_headers(student))
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_recommendations_top_n_returns_top_ranked(client):
    """top_n=2 returns the 2 highest-scoring projects."""
    db = TestingSessionLocal()
    student = create_student(db, "topn2@test.com")
    org = create_org(db, "topn2_org@test.com")
    create_profile(db, student)

    for i in range(5):
        create_project(db, org, title=f"Project {i}", status="open")

    all_response = client.get("/recommendations", headers=get_auth_headers(student))
    top2_response = client.get("/recommendations?top_n=2", headers=get_auth_headers(student))

    all_data = all_response.json()
    top2_data = top2_response.json()

    assert len(top2_data) == 2
    assert top2_data[0]["project_id"] == all_data[0]["project_id"]
    assert top2_data[1]["project_id"] == all_data[1]["project_id"]


def test_recommendations_top_n_invalid_rejected(client):
    """top_n=0 is rejected — must be >= 1."""
    db = TestingSessionLocal()
    student = create_student(db, "topninvalid@test.com")
    create_profile(db, student)

    response = client.get("/recommendations?top_n=0", headers=get_auth_headers(student))
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------

def test_recommendations_deterministic(client, db_session):
    """Same student, same projects → same ranked order on repeated calls."""
    db = db_session
    student = create_student(db, "determ@test.com")
    org = create_org(db, "determ_org@test.com")
    create_profile(db, student, skills="python,sql")

    for i in range(4):
        create_project(db, org, title=f"Project {i}", status="open")

    r1 = client.get("/recommendations", headers=get_auth_headers(student)).json()
    r2 = client.get("/recommendations", headers=get_auth_headers(student)).json()

    ids1 = [item["project_id"] for item in r1]
    ids2 = [item["project_id"] for item in r2]
    assert ids1 == ids2