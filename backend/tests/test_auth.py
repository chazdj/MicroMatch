def test_register_valid_user(client):
    """
    Ensure a user can register successfully.
    Password should not be returned in response.
    """
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
    """
    Ensure duplicate email registration returns 409 Conflict.
    """

    # First registration
    client.post(
        "/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "password123",
            "role": "student"
        },
    )

    # Duplicate attempt
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
    """
    Ensure a registered user can log in and receive a JWT token.
    """

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
    assert "access_token" in response.json()

def test_login_invalid_password(client):
    """
    Ensure login fails with incorrect password.
    """

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
    """
    Ensure organization users cannot access student-only endpoints.
    """

    # Register organization user
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