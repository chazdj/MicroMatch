import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db

# ------------------------------------------------------------------
# Test Database Configuration (SQLite)
# ------------------------------------------------------------------

# Use SQLite file-based DB for isolated testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # Required for SQLite
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ------------------------------------------------------------------
# Dependency Override
# ------------------------------------------------------------------

def override_get_db():
    """
    Overrides the production get_db dependency
    so tests use the isolated SQLite database.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Apply override globally for tests
app.dependency_overrides[get_db] = override_get_db


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------

@pytest.fixture(scope="function")
def db_session():
    """
    Provides a clean database session for each test.

    Drops and recreates all tables to ensure isolation.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def client():
    """
    Provides a FastAPI TestClient with a clean database.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with TestClient(app) as c:
        yield c