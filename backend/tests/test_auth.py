def test_register_valid_user(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "strongpassword",
            "role": "student"
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "password" not in data

def test_register_duplicate_email(client):
    # First registration
    client.post(
        "/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "password123",
            "role": "student"
        },
    )

    # Attempt duplicate registration
    response = client.post(
        "/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "newpassword",
            "role": "student"
        },
    )

    assert response.status_code == 409

def test_login_valid_user(client):
    client.post(
        "/auth/register",
        json={
            "email": "login@example.com",
            "password": "loginpassword",
            "role": "student"
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "login@example.com",
            "password": "loginpassword"
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_login_invalid_password(client):
    client.post(
        "/auth/register",
        json={
            "email": "badlogin@example.com",
            "password": "correctpass",
            "role": "student"
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "badlogin@example.com",
            "password": "wrongpass"
        },
    )

    assert response.status_code == 401

def test_role_based_access_control(client):
    # Register org user
    client.post(
        "/auth/register",
        json={
            "email": "org@example.com",
            "password": "orgpass",
            "role": "organization"
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": "org@example.com",
            "password": "orgpass"
        },
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/student/profile",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403
