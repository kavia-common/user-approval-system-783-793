from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .security import decode_token
from .db import query_one

bearer_scheme = HTTPBearer(auto_error=False)


# PUBLIC_INTERFACE
def get_current_user(creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)) -> dict:
    """Extract and validate current user from Authorization header."""
    if creds is None or not creds.scheme.lower() == "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = creds.credentials
    claims = decode_token(token)
    if not claims:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = query_one("SELECT id, email, role, is_active FROM users WHERE id = ?;", (int(claims["sub"]),))
    if not user or not user.get("is_active", 0):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User inactive or not found")
    return user


# PUBLIC_INTERFACE
def require_admin(user: dict = Depends(get_current_user)) -> dict:
    """Ensure the current user has admin role."""
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user
