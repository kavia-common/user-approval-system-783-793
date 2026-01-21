"""
API package initialization for the Social Dashboard backend.

Exposes configuration, database helpers, security utilities, dependencies,
and router modules for discoverability and easier imports.
"""

# Re-export key modules for convenience
from .config import get_settings  # noqa: F401
from .db import get_connection, query_one, query_all, execute  # noqa: F401
from .security import create_password_hash, verify_password, create_access_token, decode_token  # noqa: F401

# Routers (imported for side effects and re-export)
from . import routers_auth as auth  # noqa: F401
from . import routers_users as users  # noqa: F401
from . import routers_posts as posts  # noqa: F401
from . import routers_analytics as analytics  # noqa: F401
from . import routers_admin as admin  # noqa: F401

__all__ = [
    "get_settings",
    "get_connection",
    "query_one",
    "query_all",
    "execute",
    "create_password_hash",
    "verify_password",
    "create_access_token",
    "decode_token",
    "auth",
    "users",
    "posts",
    "analytics",
    "admin",
]
