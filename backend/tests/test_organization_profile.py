import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import User, OrganizationProfile
from app.utils.security import hash_password
from app.core.auth import create_access_token

# Test client instance
client = TestClient(app)

# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------

@pytest.fixture
def organization_user(db_session):
    """
    Create and return an organization user.
    """
    user = User(
        email="org@example.com",
        hashed_password=hash_password("password123"),
        role="organization"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def organization_token(organization_user):
    """
    Generate a JWT token for the organization user.
    """
    return create_access_token({
        "user_id": organization_user.id,
        "role": organization_user.role
    })

@pytest.fixture
def existing_organization_profile(db_session, organization_user):
    """
    Create an organization profile for GET/PUT/DELETE tests.
    """
    profile = OrganizationProfile(
        user_id=organization_user.id,
        organization_name="Tech Corp",
        industry="Software",
        website="https://techcorp.com",
        description="We build scalable systems."
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    return profile

# ------------------------------------------------------------------
# CREATE
# ------------------------------------------------------------------

def test_create_organization_profile(organization_token):
    """
    Ensure an organization can successfully create a profile.
    """
    headers = {"Authorization": f"Bearer {organization_token}"}

    payload = {
        "organization_name": "Tech Corp",
        "industry": "Software",
        "website": "https://techcorp.com",
        "description": "We build scalable systems."
    }

    response = client.post("/organization/profile", json=payload, headers=headers)

    assert response.status_code == 201
    assert response.json()["organization_name"] == "Tech Corp"

# ------------------------------------------------------------------
# GET
# ------------------------------------------------------------------

def test_get_organization_profile(organization_token, existing_organization_profile):
    """
    Ensure an organization can retrieve its profile.
    """
    headers = {"Authorization": f"Bearer {organization_token}"}

    response = client.get("/organization/profile", headers=headers)

    assert response.status_code == 200
    assert response.json()["organization_name"] == "Tech Corp"

# ------------------------------------------------------------------
# UPDATE
# ------------------------------------------------------------------

def test_update_organization_profile(organization_token, existing_organization_profile):
    """
    Ensure an organization can update profile fields.
    """
    headers = {"Authorization": f"Bearer {organization_token}"}

    payload = {
        "industry": "FinTech",
        "description": "Updated description"
    }

    response = client.put("/organization/profile", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["industry"] == "FinTech"
    assert data["description"] == "Updated description"

# ------------------------------------------------------------------
# DELETE
# ------------------------------------------------------------------

def test_delete_organization_profile(organization_token, existing_organization_profile):
    """
    Ensure an organization can delete its profile.
    """
    headers = {"Authorization": f"Bearer {organization_token}"}

    response = client.delete("/organization/profile", headers=headers)
    assert response.status_code == 204

    # Verify profile no longer exists
    follow_up = client.get("/organization/profile", headers=headers)
    assert follow_up.status_code == 404

# ------------------------------------------------------------------
# ROLE RESTRICTION
# ------------------------------------------------------------------

def test_student_cannot_access_organization_profile(db_session):
    """
    Ensure students cannot access organization-only endpoints.
    """
    student = User(
        email="student@example.com",
        hashed_password=hash_password("password123"),
        role="student"
    )

    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)

    token = create_access_token({
        "user_id": student.id,
        "role": student.role
    })

    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/organization/profile",
        json={"organization_name": "Hack Attempt"},
        headers=headers
    )

    assert response.status_code == 403