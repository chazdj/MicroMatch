# tests/test_e2e_application_workflow.py

def test_e2e_student_application_workflow(client):
    """
    TC-E2E-01 – End-to-End Student Application Workflow

    Preconditions:
    - Student and organization accounts exist
    - Project listing exists

    Steps:
    1. Student browses project listings
    2. Student submits application
    3. Organization retrieves applications
    4. Organization accepts application
    5. Student dashboard retrieves updated data

    Expected Result:
    - Application created successfully
    - Organization sees application
    - Organization accepts application
    - Student dashboard shows accepted
    """

    # ------------------------------------------------
    # Register organization
    # ------------------------------------------------

    org_data = {
        "email": "org_e2e@test.com",
        "password": "password123",
        "role": "organization"
    }

    response = client.post("/auth/register", json=org_data)
    assert response.status_code == 201

    login = client.post("/auth/login", json={
        "email": org_data["email"],
        "password": org_data["password"]
    })

    org_token = login.json()["access_token"]

    # ------------------------------------------------
    # Register student
    # ------------------------------------------------

    student_data = {
        "email": "student_e2e@test.com",
        "password": "password123",
        "role": "student"
    }

    response = client.post("/auth/register", json=student_data)
    assert response.status_code == 201

    login = client.post("/auth/login", json={
        "email": student_data["email"],
        "password": student_data["password"]
    })

    student_token = login.json()["access_token"]

    # ------------------------------------------------
    # Organization creates project
    # ------------------------------------------------

    project_payload = {
        "title": "E2E Test Project",
        "description": "Test full workflow",
        "required_skills": "Python",
        "duration": "2 weeks"
    }

    response = client.post(
        "/projects",
        json=project_payload,
        headers={"Authorization": f"Bearer {org_token}"}
    )

    assert response.status_code == 201

    project_id = response.json()["id"]

    # ------------------------------------------------
    # Student browses projects
    # ------------------------------------------------

    response = client.get("/projects")

    assert response.status_code == 200
    assert any(p["id"] == project_id for p in response.json())

    # ------------------------------------------------
    # Student applies
    # ------------------------------------------------

    response = client.post(
        "/applications",
        json={"project_id": project_id},
        headers={"Authorization": f"Bearer {student_token}"}
    )

    assert response.status_code == 201

    application_id = response.json()["id"]

    # ------------------------------------------------
    # Organization retrieves applications
    # ------------------------------------------------

    response = client.get(
        f"/projects/{project_id}/applications",
        headers={"Authorization": f"Bearer {org_token}"}
    )

    assert response.status_code == 200
    assert len(response.json()) >= 1

    # ------------------------------------------------
    # Organization accepts application
    # ------------------------------------------------

    response = client.patch(
        f"/applications/{application_id}/status",
        json={"status": "accepted"},
        headers={"Authorization": f"Bearer {org_token}"}
    )

    assert response.status_code == 200

    # ------------------------------------------------
    # Student dashboard retrieves updated data
    # ------------------------------------------------

    response = client.get(
        "/applications/me",
        headers={"Authorization": f"Bearer {student_token}"}
    )

    assert response.status_code == 200
    assert response.json()[0]["status"] == "accepted"