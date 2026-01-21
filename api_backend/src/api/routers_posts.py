from typing import List

from fastapi import APIRouter, Depends, HTTPException

from .deps import get_current_user
from .db import query_one, query_all, execute
from .schemas import PostCreate, PostOut, EngagementCreate, EngagementOut

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post("/", response_model=PostOut, summary="Create a post")
def create_post(payload: PostCreate, user: dict = Depends(get_current_user)):
    """Create a post for the current user."""
    post_id = execute("INSERT INTO posts (user_id, content, created_at) VALUES (?, ?, datetime('now'));",
                      (user["id"], payload.content))
    post = query_one("SELECT id, user_id, content, created_at FROM posts WHERE id = ?;", (post_id,))
    return post


@router.get("/me", response_model=List[PostOut], summary="List my posts")
def list_my_posts(user: dict = Depends(get_current_user)):
    """List all posts authored by the current user."""
    rows = query_all("SELECT id, user_id, content, created_at FROM posts WHERE user_id = ? ORDER BY id DESC;",
                     (user["id"],))
    return rows


@router.delete("/{post_id}", summary="Delete my post")
def delete_post(post_id: int, user: dict = Depends(get_current_user)):
    """Delete a post that belongs to the current user."""
    post = query_one("SELECT id, user_id FROM posts WHERE id = ?;", (post_id,))
    if not post or int(post["user_id"]) != int(user["id"]):
        raise HTTPException(status_code=404, detail="Post not found")
    execute("DELETE FROM posts WHERE id = ?;", (post_id,))
    return {"status": "ok", "deleted": post_id}


# Engagements
@router.post("/{post_id}/engagements", response_model=EngagementOut, summary="Engage with a post")
def create_engagement(post_id: int, payload: EngagementCreate, user: dict = Depends(get_current_user)):
    """Create an engagement (like, comment, share) for a post."""
    post = query_one("SELECT id FROM posts WHERE id = ?;", (post_id,))
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    engagement_id = execute(
        "INSERT INTO engagements (post_id, user_id, type, content, created_at) VALUES (?, ?, ?, ?, datetime('now'));",
        (post_id, user["id"], payload.type, payload.content or None),
    )
    row = query_one(
        "SELECT id, post_id, user_id, type, content, created_at FROM engagements WHERE id = ?;",
        (engagement_id,),
    )
    return row


@router.get("/{post_id}/engagements", response_model=List[EngagementOut], summary="List engagements for a post")
def list_engagements(post_id: int, user: dict = Depends(get_current_user)):
    """List engagements for a given post; allowed for any authenticated user."""
    post = query_one("SELECT id FROM posts WHERE id = ?;", (post_id,))
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    rows = query_all(
        "SELECT id, post_id, user_id, type, content, created_at FROM engagements WHERE post_id = ? ORDER BY id DESC;",
        (post_id,),
    )
    return rows
