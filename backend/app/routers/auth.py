from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas.user import UserCreate, LoginRequest, TokenResponse
from app.utils.security import hash_password, verify_password
from app.core.auth import create_access_token
from app.core.dependencies import get_current_user, require_role

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user.password)

    new_user = User(
        email=user.email,
        hashed_password=hashed_password,
        role="student"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    token_data = {"user_id": user.id, "role": user.role}
    access_token = create_access_token(token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": "You are authenticated", "user": current_user}


@router.get("/admin-only")
def admin_only(current_user: dict = Depends(require_role("admin"))):
    return {"message": "Welcome admin"}