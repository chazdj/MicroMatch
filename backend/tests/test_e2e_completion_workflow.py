# tests/test_e2e_completion_workflow.py
import pytest
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Project, Application, Deliverable, Feedback, SystemLog

# Redirect middleware DB writes to the test database
test_engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})
TestSessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(autouse=True)
def patch_middleware_session():
    with patch("app.middleware.logging_middleware.SessionLocal", TestSessionFactory):
        yield


def test_e2e_completion_workflow(client, db_session):
    """
    TC-E2E-02 — End-to-End Completion Workflow Validation

    Flow:
    1.  Register admin, org, student
    2.  Org creates project
    3.  Student browses and applies
    4.  Org retrieves and accepts application
    5.  Student checks updated application status
    6.  Student submits deliverable
    7.  Feedback is blocked before project completion (guard check)
    8.  Org retrieves deliverables
    9.  Org accepts deliverable
    10. Org marks project complete
    11. Student submits feedback (now allowed)
    12. Org submits feedback
    13. Admin views system logs
    14. DB state verified at each transition point
    """

    # --------------------------------------------------------
    # Step 1: Register and log in all three users
    # --------------------------------------------------------

    client.post("/auth/register", json={
        "email": "admin@e2e.com",
        "password": "password123",
        "role": "admin"
    })
    admin_token = client.post("/auth/login", json={
        "email": "admin@e2e.com",
        "password": "password123"
    }).json()["access_token"]

    client.post("/auth/register", json={
        "email": "org@e2e.com",
        "password": "password123",
        "role": "organization"
    })
    org_token = client.post("/auth/login", json={
        "email": "org@e2e.com",
        "password": "password123"
    }).json()["access_token"]

    client.post("/auth/register", json={
        "email": "student@e2e.com",
        "password": "password123",
        "role": "student"
    })
    student_token = client.post("/auth/login", json={
        "email": "student@e2e.com",
        "password": "password123"
    }).json()["access_token"]

    # --------------------------------------------------------
    # Step 2: Org creates a project
    # --------------------------------------------------------

    res = client.post(
        "/projects",
        json={
            "title": "E2E Completion Project",
            "description": "Full workflow validation",
            "required_skills": "Python",
            "duration": "2 weeks"
        },
        headers={"Authorization": f"Bearer {org_token}"}
    )
    assert res.status_code == 201
    project_id = res.json()["id"]
    assert res.json()["status"] == "open"

    # --------------------------------------------------------
    # Step 3: Student browses projects and applies
    # --------------------------------------------------------

    res = client.get("/projects")
    assert res.status_code == 200
    assert any(p["id"] == project_id for p in res.json())

    res = client.post(
        "/applications",
        json={"project_id": project_id},
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert res.status_code == 201
    application_id = res.json()["id"]
    assert res.json()["status"] == "pending"

    # DB check: application is pending
    db_session.expire_all()
    app_record = db_session.query(Application).filter(Application.id == application_id).first()
    assert app_record.status == "pending"

    # --------------------------------------------------------
    # Step 4: Org retrieves applications and accepts
    # --------------------------------------------------------

    res = client.get(
        f"/projects/{project_id}/applications",
        headers={"Authorization": f"Bearer {org_token}"}
    )
    assert res.status_code == 200
    assert len(res.json()) == 1

    res = client.patch(
        f"/applications/{application_id}/status",
        json={"status": "accepted"},
        headers={"Authorization": f"Bearer {org_token}"}
    )
    assert res.status_code == 200
    assert res.json()["status"] == "accepted"

    # DB check: application accepted, project closed
    db_session.expire_all()
    app_record = db_session.query(Application).filter(Application.id == application_id).first()
    assert app_record.status == "accepted"

    project_record = db_session.query(Project).filter(Project.id == project_id).first()
    assert project_record.status == "closed"

    # --------------------------------------------------------
    # Step 5: Student confirms their application is accepted
    # --------------------------------------------------------

    res = client.get(
        "/applications/me",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert res.status_code == 200
    assert res.json()[0]["status"] == "accepted"

    # --------------------------------------------------------
    # Step 6: Student submits deliverable
    # --------------------------------------------------------

    res = client.post(
        f"/applications/{application_id}/deliverables",
        json={"content": "Here is my completed work."},
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert res.status_code == 201
    deliverable_id = res.json()["id"]
    assert res.json()["status"] == "submitted"

    # DB check: deliverable is submitted
    db_session.expire_all()
    deliverable_record = db_session.query(Deliverable).filter(Deliverable.id == deliverable_id).first()
    assert deliverable_record.status == "submitted"

    # --------------------------------------------------------
    # Step 7: Feedback is blocked before project completion
    # --------------------------------------------------------

    res = client.post(
        "/feedback",
        json={"project_id": project_id, "rating": 5, "comment": "Too early!"},
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert res.status_code == 400
    assert "completed" in res.json()["detail"].lower()

    # --------------------------------------------------------
    # Step 8: Org retrieves deliverables
    # --------------------------------------------------------

    res = client.get(
        f"/deliverables/projects/{project_id}",
        headers={"Authorization": f"Bearer {org_token}"}
    )
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["status"] == "submitted"

    # --------------------------------------------------------
    # Step 9: Org accepts deliverable
    # --------------------------------------------------------

    res = client.put(
        f"/deliverables/{deliverable_id}/review",
        json={"status": "accepted", "feedback": "Great work!"},
        headers={"Authorization": f"Bearer {org_token}"}
    )
    assert res.status_code == 200
    assert res.json()["status"] == "accepted"

    # DB check: deliverable accepted
    db_session.expire_all()
    deliverable_record = db_session.query(Deliverable).filter(Deliverable.id == deliverable_id).first()
    assert deliverable_record.status == "accepted"

    # --------------------------------------------------------
    # Step 10: Org marks project complete
    # --------------------------------------------------------

    res = client.put(
        f"/projects/{project_id}/complete",
        headers={"Authorization": f"Bearer {org_token}"}
    )
    assert res.status_code == 200
    assert res.json()["status"] == "completed"

    # DB check: project is completed
    db_session.expire_all()
    project_record = db_session.query(Project).filter(Project.id == project_id).first()
    assert project_record.status == "completed"

    # --------------------------------------------------------
    # Step 11: Student submits feedback (now allowed)
    # --------------------------------------------------------

    res = client.post(
        "/feedback",
        json={"project_id": project_id, "rating": 5, "comment": "Great experience!"},
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert res.status_code == 201
    assert res.json()["rating"] == 5

    # --------------------------------------------------------
    # Step 12: Org submits feedback
    # --------------------------------------------------------

    res = client.post(
        "/feedback",
        json={"project_id": project_id, "rating": 4, "comment": "Good student."},
        headers={"Authorization": f"Bearer {org_token}"}
    )
    assert res.status_code == 201
    assert res.json()["rating"] == 4

    # DB check: two feedback entries exist
    db_session.expire_all()
    feedback_entries = db_session.query(Feedback).filter(Feedback.project_id == project_id).all()
    assert len(feedback_entries) == 2

    # --------------------------------------------------------
    # Step 13: Admin views system logs
    # --------------------------------------------------------

    res = client.get(
        "/admin/logs",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 200
    logs = res.json()
    assert len(logs) > 0

    logged_endpoints = [log["endpoint"] for log in logs]
    assert any("/projects" in e for e in logged_endpoints)
    assert any("/applications" in e for e in logged_endpoints)
    assert any("/feedback" in e for e in logged_endpoints)
    assert any("/deliverables" in e for e in logged_endpoints)

    # Verify at least one log has a user_id (authenticated request was captured)
    assert any(log["user_id"] is not None for log in logs)

    # Verify both success and expected error were logged
    status_codes = [log["status_code"] for log in logs]
    assert 201 in status_codes   # successful creates
    assert 400 in status_codes   # feedback blocked before completion
