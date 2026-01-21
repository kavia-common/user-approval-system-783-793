from fastapi import APIRouter, Depends

from .deps import get_current_user, require_admin
from .db import query_one, query_all
from .schemas import AnalyticsSummary

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/me", response_model=dict, summary="My analytics overview")
def my_analytics(user: dict = Depends(get_current_user)):
    """Return simple analytics for the current user: post count and engagement totals."""
    total_posts = query_one("SELECT COUNT(*) AS c FROM posts WHERE user_id = ?;", (user["id"],))["c"]
    total_engagements = query_one(
        "SELECT COUNT(*) AS c FROM engagements WHERE post_id IN (SELECT id FROM posts WHERE user_id = ?);",
        (user["id"],),
    )["c"]
    recent = query_all(
        "SELECT p.id, p.content, "
        "(SELECT COUNT(*) FROM engagements e WHERE e.post_id = p.id) AS engagements_count "
        "FROM posts p WHERE p.user_id = ? ORDER BY p.id DESC LIMIT 5;",
        (user["id"],),
    )
    return {
        "total_posts": total_posts,
        "total_engagements": total_engagements,
        "recent_posts": recent,
    }


@router.get("/platform", response_model=AnalyticsSummary, summary="Platform analytics (admin)")
def platform_analytics(_: dict = Depends(require_admin)):
    """Aggregate analytics across the platform for administrators."""
    total_users = query_one("SELECT COUNT(*) AS c FROM users;", ())["c"]
    total_posts = query_one("SELECT COUNT(*) AS c FROM posts;", ())["c"]
    total_engagements = query_one("SELECT COUNT(*) AS c FROM engagements;", ())["c"]
    # Top posts by engagements
    top_posts = query_all(
        "SELECT p.id, p.content, u.email AS author_email, "
        "(SELECT COUNT(*) FROM engagements e WHERE e.post_id = p.id) AS engagements_count "
        "FROM posts p JOIN users u ON u.id = p.user_id "
        "ORDER BY engagements_count DESC, p.id DESC LIMIT 10;",
        (),
    )
    # Recent 7-day growth
    recent_growth = {
        "users": query_one("SELECT COUNT(*) AS c FROM users WHERE created_at >= datetime('now','-7 day');", ())["c"]
        if query_one("SELECT name FROM pragma_table_info('users') WHERE name='created_at';", ()) else 0,
        "posts": query_one("SELECT COUNT(*) AS c FROM posts WHERE created_at >= datetime('now','-7 day');", ())["c"],
        "engagements": query_one(
            "SELECT COUNT(*) AS c FROM engagements WHERE created_at >= datetime('now','-7 day');", ()
        )["c"],
    }
    return {
        "total_users": total_users,
        "total_posts": total_posts,
        "total_engagements": total_engagements,
        "top_posts": top_posts,
        "recent_growth": recent_growth,
    }
