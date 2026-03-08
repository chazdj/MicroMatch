# tests/test_dependencies.py

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_protected_route_without_token():
    response = client.get("/auth/protected")

    assert response.status_code == 403 or response.status_code == 401


def test_admin_only_wrong_role():
    response = client.get(
        "/auth/admin-only",
        headers={"Authorization": "Bearer invalidtoken"}
    )

    assert response.status_code in [401, 403]