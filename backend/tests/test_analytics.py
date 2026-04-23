import pytest
from app.models import User, Project, Application, Feedback
from app.schemas.user import UserRole
from app.utils.security import hash_password


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


def create_application(db, student_id, project_id, status="pending"):
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
# Student Analytics — GET /analytics/student
# ---------------------------------------------------------------

class TestStudentAnalytics:

    def test_returns_zeroes_for_new_student(self, client, db_session):
        """New student with no activity returns all zeros."""
        create_user(db_session, "student@test.com", UserRole.student)
        token = login(client, "student@test.com")

        resp = client.get("/analytics/student", headers=auth(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["applications_submitted"] == 0
        assert data["accepted_applications"] == 0
        assert data["completed_projects"] == 0
        assert data["average_feedback_rating"] is None

    def test_counts_applications_correctly(self, client, db_session):
        """Submitted, accepted, and completed counts are accurate."""
        org = create_user(db_session, "org@test.com", UserRole.organization)
        student = create_user(db_session, "student@test.com", UserRole.student)

        p1 = create_project(db_session, org.id, status="open")
        p2 = create_project(db_session, org.id, status="open")
        p3 = create_project(db_session, org.id, status="completed")

        create_application(db_session, student.id, p1.id, status="pending")
        create_application(db_session, student.id, p2.id, status="accepted")
        create_application(db_session, student.id, p3.id, status="accepted")

        token = login(client, "student@test.com")
        resp = client.get("/analytics/student", headers=auth(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["applications_submitted"] == 3
        assert data["accepted_applications"] == 2
        assert data["completed_projects"] == 1

    def test_average_feedback_rating(self, client, db_session):
        """Average rating is calculated correctly across multiple feedback entries."""
        org = create_user(db_session, "org@test.com", UserRole.organization)
        student = create_user(db_session, "student@test.com", UserRole.student)

        p1 = create_project(db_session, org.id, status="completed")
        p2 = create_project(db_session, org.id, status="completed")
        create_feedback(db_session, student.id, p1.id, rating=4)
        create_feedback(db_session, student.id, p2.id, rating=2)

        token = login(client, "student@test.com")
        resp = client.get("/analytics/student", headers=auth(token))
        assert resp.status_code == 200
        assert resp.json()["average_feedback_rating"] == 3.0

    def test_organization_blocked(self, client, db_session):
        """Organization cannot access student analytics."""
        create_user(db_session, "org@test.com", UserRole.organization)
        token = login(client, "org@test.com")

        resp = client.get("/analytics/student", headers=auth(token))
        assert resp.status_code == 403

    def test_unauthenticated_blocked(self, client, db_session):
        """Unauthenticated request is rejected."""
        resp = client.get("/analytics/student")
        assert resp.status_code == 401

    def test_only_counts_own_applications(self, client, db_session):
        """Student only sees their own applications, not others'."""
        org = create_user(db_session, "org@test.com", UserRole.organization)
        student1 = create_user(db_session, "s1@test.com", UserRole.student)
        student2 = create_user(db_session, "s2@test.com", UserRole.student)

        p = create_project(db_session, org.id)
        create_application(db_session, student1.id, p.id, status="accepted")
        create_application(db_session, student2.id, p.id, status="accepted")

        token = login(client, "s1@test.com")
        resp = client.get("/analytics/student", headers=auth(token))
        assert resp.status_code == 200
        assert resp.json()["applications_submitted"] == 1


# ---------------------------------------------------------------
# Organization Analytics — GET /analytics/organization
# ---------------------------------------------------------------

class TestOrganizationAnalytics:

    def test_returns_zeroes_for_new_org(self, client, db_session):
        """New org with no projects returns all zeros."""
        create_user(db_session, "org@test.com", UserRole.organization)
        token = login(client, "org@test.com")

        resp = client.get("/analytics/organization", headers=auth(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_projects_posted"] == 0
        assert data["active_projects"] == 0
        assert data["completed_projects"] == 0
        assert data["total_applicants"] == 0

    def test_counts_projects_by_status(self, client, db_session):
        """Active and completed project counts are separated correctly."""
        org = create_user(db_session, "org@test.com", UserRole.organization)

        create_project(db_session, org.id, status="open")
        create_project(db_session, org.id, status="open")
        create_project(db_session, org.id, status="completed")

        token = login(client, "org@test.com")
        resp = client.get("/analytics/organization", headers=auth(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_projects_posted"] == 3
        assert data["active_projects"] == 2
        assert data["completed_projects"] == 1

    def test_total_applicants_counts_unique_students(self, client, db_session):
        """Same student applying to two projects counts as 1 unique applicant."""
        org = create_user(db_session, "org@test.com", UserRole.organization)
        s1 = create_user(db_session, "s1@test.com", UserRole.student)
        s2 = create_user(db_session, "s2@test.com", UserRole.student)

        p1 = create_project(db_session, org.id)
        p2 = create_project(db_session, org.id)

        # s1 applies to both projects — should count as 1 unique applicant
        create_application(db_session, s1.id, p1.id)
        create_application(db_session, s1.id, p2.id)
        # s2 applies to one project
        create_application(db_session, s2.id, p1.id)

        token = login(client, "org@test.com")
        resp = client.get("/analytics/organization", headers=auth(token))
        assert resp.status_code == 200
        assert resp.json()["total_applicants"] == 2

    def test_only_counts_own_projects(self, client, db_session):
        """Org only sees metrics for their own projects, not other orgs'."""
        org1 = create_user(db_session, "org1@test.com", UserRole.organization)
        org2 = create_user(db_session, "org2@test.com", UserRole.organization)

        create_project(db_session, org1.id, status="open")
        create_project(db_session, org2.id, status="open")
        create_project(db_session, org2.id, status="open")

        token = login(client, "org1@test.com")
        resp = client.get("/analytics/organization", headers=auth(token))
        assert resp.status_code == 200
        assert resp.json()["total_projects_posted"] == 1

    def test_student_blocked(self, client, db_session):
        """Student cannot access organization analytics."""
        create_user(db_session, "student@test.com", UserRole.student)
        token = login(client, "student@test.com")

        resp = client.get("/analytics/organization", headers=auth(token))
        assert resp.status_code == 403

    def test_unauthenticated_blocked(self, client, db_session):
        """Unauthenticated request is rejected."""
        resp = client.get("/analytics/organization")
        assert resp.status_code == 401