# tests/test_auth_token_utils.py

from datetime import timedelta
from app.core.auth import create_access_token, decode_access_token


def test_create_token_with_custom_expiry():
    token = create_access_token(
        {"user_id": 1},
        expires_delta=timedelta(minutes=5)
    )

    decoded = decode_access_token(token)

    assert decoded["user_id"] == 1
    assert "exp" in decoded


def test_decode_invalid_token_returns_none():
    invalid_token = "this.is.not.valid"

    result = decode_access_token(invalid_token)

    assert result is None