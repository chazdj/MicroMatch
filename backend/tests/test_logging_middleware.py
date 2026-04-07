import pytest
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import User, SystemLog
from app.utils.security import hash_password
from app.core.auth import create_access_token

# Mirror the conftest test DB so middleware writes go to the same SQLite file
test_engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})
TestSessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(autouse=True)
def patch_middleware_session():
    """Redirect middleware's SessionLocal to the test database."""
    with patch("app.middleware.logging_middleware.SessionLocal", TestSessionFactory):
        yield


def test_unauthenticated_request_is_logged(client, db_session):
    """Unauthenticated request should create a log entry with null user_id and role."""
    client.post(
        "/auth/register",
        json={"email": "log@test.com", "password": "password123", "role": "student"}
    )

    log = db_session.query(SystemLog).first()
    assert log is not None
    assert log.user_id is None
    assert log.role is None
    assert log.endpoint == "/auth/register"
    assert log.method == "POST"
    assert log.status_code == 201


def test_authenticated_request_logs_user_id_and_role(client, db_session):
    """Authenticated request should capture user_id and role from the JWT."""
    user = User(
        email="authlog@test.com",
        hashed_password=hash_password("password123"),
        role="student"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = create_access_token({"user_id": user.id, "role": "student"})

    client.get(
        "/auth/protected",
        headers={"Authorization": f"Bearer {token}"}
    )

    log = db_session.query(SystemLog).first()
    assert log is not None
    assert log.user_id == user.id
    assert log.role == "student"
    assert log.endpoint == "/auth/protected"
    assert log.method == "GET"


def test_failed_request_logs_error_status_code(client, db_session):
    """A 401 response should still be logged with the correct status code."""
    client.get("/auth/protected")  # no token -> 401

    log = db_session.query(SystemLog).first()
    assert log is not None
    assert log.status_code == 401
    assert log.user_id is None


def test_multiple_requests_create_multiple_log_entries(client, db_session):
    """Each request should produce its own log entry."""
    client.post(
        "/auth/register",
        json={"email": "a@test.com", "password": "password123", "role": "student"}
    )
    client.post(
        "/auth/register",
        json={"email": "b@test.com", "password": "password123", "role": "student"}
    )

    logs = db_session.query(SystemLog).all()
    assert len(logs) == 2


def test_log_timestamp_is_set(client, db_session):
    """Every log entry must have a non-null timestamp."""
    client.post(
        "/auth/register",
        json={"email": "ts@test.com", "password": "password123", "role": "student"}
    )

    log = db_session.query(SystemLog).first()
    assert log is not None
    assert log.timestamp is not None


def test_log_records_correct_http_method(client, db_session):
    """Log entry must record the actual HTTP method used."""
    client.get("/auth/protected")

    log = db_session.query(SystemLog).first()
    assert log is not None
    assert log.method == "GET"
