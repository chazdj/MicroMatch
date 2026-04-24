import pytest
from app.models import User, StudentProfile, Project, Application, Feedback
from app.schemas.user import UserRole
from app.utils.security import hash_password
from app.utils.badges import compute_badges, award_badges


# ---------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------

def create_user(db, email, role=UserRole.student):
    user = User(
        email=email,
        hashed_password=hash_password("password123"),
        role=role,
        name="Test",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_profile(db, user_id):
    p = StudentProfile(
        user_id=user_id, university="MIT",
        major="CS", graduation_year=2025
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def create_completed_project(db, org_id, student_id):
    project = Project(
        organization_id=org_id, title="P",
        description="D", status="completed"
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    app = Application(
        student_id=student_id,
        project_id=project.id,
        status="accepted"
    )
    db.add(app)
    db.commit()
    return project


def create_feedback(db, user_id, project_id, rating):
    f = Feedback(
        user_id=user_id, project_id=project_id,
        rating=rating, comment="Good"
    )
    db.add(f)
    db.commit()


# ---------------------------------------------------------------
# Unit tests — compute_badges
# ---------------------------------------------------------------

class TestComputeBadges:

    def test_no_badges_for_new_student(self, db_session):
        org = create_user(db_session, "org@test.com", UserRole.organization)
        student = create_user(db_session, "s@test.com")
        create_profile(db_session, student.id)

        result = compute_badges(student.id, db_session)
        assert result == ""

    def test_first_project_badge(self, db_session):
        org = create_user(db_session, "org@test.com", UserRole.organization)
        student = create_user(db_session, "s@test.com")
        create_profile(db_session, student.id)
        create_completed_project(db_session, org.id, student.id)

        badges = compute_badges(student.id, db_session).split(",")
        assert "first_project" in badges

    def test_three_projects_badge(self, db_session):
        org = create_user(db_session, "org@test.com", UserRole.organization)
        student = create_user(db_session, "s@test.com")
        create_profile(db_session, student.id)

        for _ in range(3):
            create_completed_project(db_session, org.id, student.id)

        badges = compute_badges(student.id, db_session).split(",")
        assert "first_project" in badges
        assert "three_projects" in badges

    def test_top_rated_badge(self, db_session):
        org = create_user(db_session, "org@test.com", UserRole.organization)
        student = create_user(db_session, "s@test.com")
        create_profile(db_session, student.id)
        p = create_completed_project(db_session, org.id, student.id)
        create_feedback(db_session, student.id, p.id, rating=5)

        badges = compute_badges(student.id, db_session).split(",")
        assert "top_rated" in badges

    def test_top_rated_not_awarded_below_threshold(self, db_session):
        org = create_user(db_session, "org@test.com", UserRole.organization)
        student = create_user(db_session, "s@test.com")
        create_profile(db_session, student.id)
        p = create_completed_project(db_session, org.id, student.id)
        create_feedback(db_session, student.id, p.id, rating=3)

        badges = compute_badges(student.id, db_session)
        assert "top_rated" not in badges

    def test_rising_star_badge(self, db_session):
        org = create_user(db_session, "org@test.com", UserRole.organization)
        student = create_user(db_session, "s@test.com")
        create_profile(db_session, student.id)

        for _ in range(3):
            p = create_completed_project(db_session, org.id, student.id)
            create_feedback(db_session, student.id, p.id, rating=5)

        badges = compute_badges(student.id, db_session).split(",")
        assert "rising_star" in badges

    def test_badges_accumulate(self, db_session):
        """All milestone badges stack — completing 10 also gives 1 and 3."""
        org = create_user(db_session, "org@test.com", UserRole.organization)
        student = create_user(db_session, "s@test.com")
        create_profile(db_session, student.id)

        for _ in range(10):
            create_completed_project(db_session, org.id, student.id)

        badges = compute_badges(student.id, db_session).split(",")
        assert "first_project" in badges
        assert "three_projects" in badges
        assert "ten_projects" in badges


# ---------------------------------------------------------------
# Unit tests — award_badges
# ---------------------------------------------------------------

class TestAwardBadges:

    def test_award_badges_saves_to_profile(self, db_session):
        org = create_user(db_session, "org@test.com", UserRole.organization)
        student = create_user(db_session, "s@test.com")
        profile = create_profile(db_session, student.id)
        create_completed_project(db_session, org.id, student.id)

        award_badges(student.id, db_session)
        db_session.commit()
        db_session.refresh(profile)

        assert "first_project" in (profile.badges or "")

    def test_award_badges_no_op_without_profile(self, db_session):
        """Should not raise if student has no profile."""
        student = create_user(db_session, "s@test.com")
        award_badges(student.id, db_session)  # should not raise

    def test_badges_cannot_be_set_via_enhance_endpoint(self, client, db_session):
        """Enhance endpoint no longer accepts badges field."""
        student = create_user(db_session, "s@test.com")
        create_profile(db_session, student.id)

        resp = client.post(
            "/auth/login",
            json={"email": "s@test.com", "password": "password123"}
        )
        token = resp.json()["access_token"]

        resp = client.put(
            "/student/profile/enhance",
            json={"badges": "fake_badge"},
            headers={"Authorization": f"Bearer {token}"},
        )
        # badges field is ignored — profile.badges should remain None/empty
        assert resp.status_code == 200
        assert resp.json().get("badges") in (None, "")