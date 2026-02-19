from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.core.auth import decode_access_token

# OAuth2 scheme for token extraction from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Validates the JWT, extracts the user_id, and loads the user from the database.

    Raises:
        - 401 if token is invalid or missing required fields
        - 404 if the user no longer exists
    """

    # Decode and validate the token, extracting the payload
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    # Extract user_id from the token payload
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    # Look up the authenticated user in the database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        # Token is valid but user no longer exists (e.g., deleted account)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


def require_role(required_role: str):
    """ 
    Dependency factory that enforces role-based access control. 
        - Accepts either Enum roles or string roles. 
        - Case-insensitive comparison. 
        
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        
        # Handles Enum OR string roles safely
        role_value = getattr(current_user.role, "value", current_user.role)

        # Reject if the user's role does not match the required role
        if role_value.lower() != required_role.lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden"
            )

        return current_user

    return role_checker