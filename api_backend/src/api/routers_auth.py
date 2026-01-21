from fastapi import APIRouter, HTTPException, status
from pydantic import EmailStr

from .db import query_one, execute
from .security import create_password_hash, verify_password, create_access_token
from .schemas import RegisterRequest, LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _get_user_by_email(email: EmailStr) -> dict | None:
    return query_one("SELECT id, email, password_hash, role, is_active FROM users WHERE email = ?;", (str(email),))


@router.post("/register", response_model=TokenResponse, summary="Register a new user")
def register(payload: RegisterRequest):
    """Create a new user and profile, returning an auth token."""
    existing = _get_user_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    pwd_hash = create_password_hash(payload.password)
    user_id = execute(
        "INSERT INTO users (email, password_hash, role, is_active) VALUES (?, ?, 'user', 1);",
        (str(payload.email), pwd_hash),
    )
    if user_id <= 0:
        raise HTTPException(status_code=500, detail="Failed to create user")

    # Create profile
    execute(
        "INSERT INTO profiles (user_id, full_name, bio, avatar_url) VALUES (?, ?, '', '');",
        (user_id, payload.full_name),
    )

    token = create_access_token(subject=str(user_id), role="user")
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse, summary="Login and retrieve JWT")
def login(payload: LoginRequest):
    """Authenticate a user by email/password and return JWT token."""
    user = _get_user_by_email(payload.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not user.get("is_active", 0):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")

    token = create_access_token(subject=str(user["id"]), role=user["role"])
    return TokenResponse(access_token=token)
