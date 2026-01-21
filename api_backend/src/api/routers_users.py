from typing import List

from fastapi import APIRouter, Depends, HTTPException

from .deps import get_current_user, require_admin
from .db import query_one, query_all, execute
from .schemas import UserOut, ProfileOut, ProfileUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserOut, summary="Get current user")
def get_me(user: dict = Depends(get_current_user)):
    """Return the authenticated user's basic record."""
    return {
        "id": user["id"],
        "email": user["email"],
        "role": user["role"],
        "is_active": bool(user["is_active"]),
    }


@router.get("/me/profile", response_model=ProfileOut, summary="Get current user's profile")
def get_my_profile(user: dict = Depends(get_current_user)):
    """Return the authenticated user's profile."""
    profile = query_one("SELECT user_id, full_name, bio, avatar_url FROM profiles WHERE user_id = ?;", (user["id"],))
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.put("/me/profile", response_model=ProfileOut, summary="Update current user's profile")
def update_my_profile(update: ProfileUpdate, user: dict = Depends(get_current_user)):
    """Update profile fields for the current user."""
    existing = query_one("SELECT user_id FROM profiles WHERE user_id = ?;", (user["id"],))
    if not existing:
        # create if missing
        execute(
            "INSERT INTO profiles (user_id, full_name, bio, avatar_url) VALUES (?, ?, ?, ?);",
            (user["id"], update.full_name or "", update.bio or "", update.avatar_url or ""),
        )
    else:
        # build dynamic update
        fields = []
        params = []
        if update.full_name is not None:
            fields.append("full_name = ?")
            params.append(update.full_name)
        if update.bio is not None:
            fields.append("bio = ?")
            params.append(update.bio)
        if update.avatar_url is not None:
            fields.append("avatar_url = ?")
            params.append(update.avatar_url)
        if fields:
            params.append(user["id"])
            execute(f"UPDATE profiles SET {', '.join(fields)} WHERE user_id = ?;", tuple(params))

    profile = query_one("SELECT user_id, full_name, bio, avatar_url FROM profiles WHERE user_id = ?;", (user["id"],))
    return profile


@router.get("/", response_model=List[UserOut], summary="List users (admin)")
def list_users(_: dict = Depends(require_admin)):
    """List all users (admin only)."""
    rows = query_all("SELECT id, email, role, is_active FROM users ORDER BY id DESC;")
    return [
        {
            "id": r["id"],
            "email": r["email"],
            "role": r["role"],
            "is_active": bool(r["is_active"]),
        }
        for r in rows
    ]


@router.put("/{user_id}/activate", summary="Activate or deactivate a user (admin)")
def set_active(user_id: int, active: bool, _: dict = Depends(require_admin)):
    """Set user active state (admin only)."""
    existing = query_one("SELECT id FROM users WHERE id = ?;", (user_id,))
    if not existing:
        raise HTTPException(status_code=404, detail="User not found")
    execute("UPDATE users SET is_active = ? WHERE id = ?;", (1 if active else 0, user_id))
    return {"status": "ok", "user_id": user_id, "is_active": active}


@router.put("/{user_id}/role", summary="Change user role (admin)")
def change_role(user_id: int, role: str, _: dict = Depends(require_admin)):
    """Change user role between 'user' and 'admin'."""
    if role not in ("user", "admin"):
        raise HTTPException(status_code=400, detail="Invalid role")
    existing = query_one("SELECT id FROM users WHERE id = ?;", (user_id,))
    if not existing:
        raise HTTPException(status_code=404, detail="User not found")
    execute("UPDATE users SET role = ? WHERE id = ?;", (role, user_id))
    return {"status": "ok", "user_id": user_id, "role": role}
