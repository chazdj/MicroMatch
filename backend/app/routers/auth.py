from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas.user import UserCreate, LoginRequest, TokenResponse
from app.utils.security import hash_password, verify_password
from app.core.auth import create_access_token
from app.core.dependencies import get_current_user, require_role
from app.schemas.user import UserRole

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201)
def register(
    user: UserCreate, 
    db: Session = Depends(get_db)):
    """
    Registers a new user.

    - Ensures email is unique
    - Hashes password before storing
    - Returns only safe fields (email + role)
    """

    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")

    # Hash the password before storing
    hashed_password = hash_password(user.password)

    # Create the user
    new_user = User(
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # tests expect email and no password in response
    return {"email": new_user.email, "role": new_user.role}

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates a user and returns a JWT access token.
    """

    # Find the user by email
    user = db.query(User).filter(User.email == data.email).first()

    # Validate credentials
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Create JWT token with user ID and role
    token_data = {"user_id": user.id, "role": user.role.value}
    access_token = create_access_token(token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    """
    Example endpoint showing how authenticated routes work.
    """
    return {"message": "You are authenticated", "user": current_user}


@router.get("/admin-only")
def admin_only(current_user: dict = Depends(require_role(UserRole.admin))):
    """
    Example role-restricted endpoint.
    """
    return {"message": "Welcome admin"}