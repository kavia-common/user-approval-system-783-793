from fastapi import APIRouter, Depends, HTTPException

from .deps import require_admin
from .db import query_one, execute

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.delete("/posts/{post_id}", summary="Admin delete any post")
def admin_delete_post(post_id: int, _: dict = Depends(require_admin)):
    """Delete a post by id as admin."""
    existing = query_one("SELECT id FROM posts WHERE id = ?;", (post_id,))
    if not existing:
        raise HTTPException(status_code=404, detail="Post not found")
    execute("DELETE FROM posts WHERE id = ?;", (post_id,))
    return {"status": "ok", "deleted": post_id}


@router.delete("/users/{user_id}", summary="Admin delete user")
def admin_delete_user(user_id: int, _: dict = Depends(require_admin)):
    """Delete a user and cascade related data if FK constraints are set."""
    existing = query_one("SELECT id FROM users WHERE id = ?;", (user_id,))
    if not existing:
        raise HTTPException(status_code=404, detail="User not found")
    execute("DELETE FROM users WHERE id = ?;", (user_id,))
    return {"status": "ok", "deleted": user_id}
