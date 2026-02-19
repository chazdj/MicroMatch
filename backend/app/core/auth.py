from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from jose import JWTError

# Secret key and algorithm for JWT encoding/decoding
SECRET_KEY = "your-super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Creates a signed JWT access token.

    - `data` contains custom payload fields (e.g., user_id, role)
    - `expires_delta` optionally overrides the default expiration time
    """

    # Copy payload data to avoid mutating the original
    to_encode = data.copy()

    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Default expiration window
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Add expiration claim to payload
    to_encode.update({"exp": expire})

    # Encode and sign the JWT token
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    """
    Decodes and verifies a JWT.

    Returns:
        - payload dict if valid
        - None if token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        # Any decode/validation error results in None
        return None