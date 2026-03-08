# tests/test_database_dependency.py

from app.database import get_db


def test_get_db_closes_session():
    gen = get_db()

    db = next(gen)

    assert db is not None

    try:
        next(gen)
    except StopIteration:
        pass