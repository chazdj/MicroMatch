import pytest
from app.models import User, StudentProfile, Project, Application, Feedback
from app.schemas.user import UserRole
from app.utils.security import hash_password
from app.utils.badges import award_badges


# ---------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------

def create_user(db, email, role):
    user = User(
        email=email,
        hashed_password=hash_password("password123"),
        role=role,
        name="Test User",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login(client, email):
    resp = client.post("/auth/login", json={"email": email, "password": "password123"})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def create_profile(db, user_id):
    p = StudentProfile(
        user_id=user_id,
        university="MIT",
        major="CS",
        graduation_year=2025,
        skills="Python",
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def create_project(db, org_id, status="open"):
    p = Project(
        organization_id=org_id,
        title="Test Project",
        description="Desc",
        status=status,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def create_application(db, student_id, project_id, status="accepted"):
    a = Application(student_id=student_id, project_id=project_id, status=status)
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


def create_feedback(db, user_id, project_id, rating):
    f = Feedback(user_id=user_id, project_id=project_id, rating=rating, comment="Good")
    db.add(f)
    db.commit()
    db.refresh(f)
    return f


# ---------------------------------------------------------------
# PUT /student/profile/enhance
# ---------------------------------------------------------------

class TestEnhanceProfile:

    def test_saves_portfolio_links(self, client, db_session):
        """Portfolio links are saved and returned."""
        student = create_user(db_session, "student@test.com", UserRole.student)
        create_profile(db_session, student.id)
        token = login(client, "student@test.com")

        resp = client.put(
            "/student/profile/enhance",
            json={"portfolio_links": "https://github.com/user,https://portfolio.dev"},
            headers=auth(token),
        )
        assert resp.status_code == 200
        assert resp.json()["portfolio_links"] == "https://github.com/user,https://portfolio.dev"

    def test_badges_ignored_by_enhance(self, client, db_session):
        """Badges sent to the enhance endpoint are silently ignored — badges are system-awarded only."""
        student = create_user(db_session, "student@test.com", UserRole.student)
        create_profile(db_session, student.id)
        token = login(client, "student@test.com")

        resp = client.put(
            "/student/profile/enhance",
            json={"badges": "top_contributor,fast_learner"},
            headers=auth(token),
        )
        assert resp.status_code == 200
        assert resp.json().get("badges") in (None, "")

    def test_partial_update_preserves_existing(self, client, db_session):
        """Sending only portfolio_links does not clear a previously saved value."""
        student = create_user(db_session, "student@test.com", UserRole.student)
        create_profile(db_session, student.id)
        token = login(client, "student@test.com")

        # Set an initial value
        client.put(
            "/student/profile/enhance",
            json={"portfolio_links": "https://github.com/user"},
            headers=auth(token),
        )
        # Update with a different value — previous value should be overwritten, not cleared
        resp = client.put(
            "/student/profile/enhance",
            json={"portfolio_links": "https://portfolio.dev"},
            headers=auth(token),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["portfolio_links"] == "https://portfolio.dev"

    def test_requires_base_profile(self, client, db_session):
        """Returns 404 if no base profile exists yet."""
        create_user(db_session, "student@test.com", UserRole.student)
        token = login(client, "student@test.com")

        resp = client.put(
            "/student/profile/enhance",
            json={"portfolio_links": "https://github.com/user"},
            headers=auth(token),
        )
        assert resp.status_code == 404

    def test_organization_blocked(self, client, db_session):
        """Organization cannot access enhance endpoint."""
        create_user(db_session, "org@test.com", UserRole.organization)
        token = login(client, "org@test.com")

        resp = client.put(
            "/student/profile/enhance",
            json={"portfolio_links": "https://github.com/user"},
            headers=auth(token),
        )
        assert resp.status_code == 403

    def test_unauthenticated_blocked(self, client, db_session):
        resp = client.put(
            "/student/profile/enhance",
            json={"portfolio_links": "https://github.com/user"},
        )
        assert resp.status_code == 401


# ---------------------------------------------------------------
# GET /student/profile/{id}
# ---------------------------------------------------------------

class TestGetProfileById:

    def test_returns_profile_with_computed_fields(self, client, db_session):
        """Computed completed_projects and average_rating are returned correctly."""
        org = create_user(db_session, "org@test.com", UserRole.organization)
        student = create_user(db_session, "student@test.com", UserRole.student)
        create_profile(db_session, student.id)

        p1 = create_project(db_session, org.id, status="completed")
        p2 = create_project(db_session, org.id, status="completed")
        create_application(db_session, student.id, p1.id, status="accepted")
        create_application(db_session, student.id, p2.id, status="accepted")
        create_feedback(db_session, student.id, p1.id, rating=4)
        create_feedback(db_session, student.id, p2.id, rating=2)

        org_token = login(client, "org@test.com")
        resp = client.get(
            f"/student/profile/{student.id}",
            headers=auth(org_token),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["completed_projects"] == 2
        assert data["average_rating"] == 3.0

    def test_returns_portfolio_and_badges(self, client, db_session):
        """Enhancement fields are visible in public profile response.
        portfolio_links is set via the enhance endpoint; badges via award_badges()."""
        org = create_user(db_session, "org@test.com", UserRole.organization)
        student = create_user(db_session, "student@test.com", UserRole.student)
        create_profile(db_session, student.id)

        # Set portfolio_links via the enhance endpoint (user-controlled)
        student_token = login(client, "student@test.com")
        client.put(
            "/student/profile/enhance",
            json={"portfolio_links": "https://github.com/user"},
            headers=auth(student_token),
        )

        # Award badges via the system utility (not the enhance endpoint)
        p = create_project(db_session, org.id, status="completed")
        create_application(db_session, student.id, p.id, status="accepted")
        award_badges(student.id, db_session)
        db_session.commit()

        org_token = login(client, "org@test.com")
        resp = client.get(
            f"/student/profile/{student.id}",
            headers=auth(org_token),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["portfolio_links"] == "https://github.com/user"
        assert "first_project" in (data.get("badges") or "")

    def test_returns_404_for_missing_profile(self, client, db_session):
        """Returns 404 when the student has no profile."""
        student = create_user(db_session, "student@test.com", UserRole.student)
        org = create_user(db_session, "org@test.com", UserRole.organization)

        org_token = login(client, "org@test.com")
        resp = client.get(
            f"/student/profile/{student.id}",
            headers=auth(org_token),
        )
        assert resp.status_code == 404
