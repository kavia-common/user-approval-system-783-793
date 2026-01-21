from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from . import routers_auth
from . import routers_users
from . import routers_posts
from . import routers_analytics
from . import routers_admin

# Create FastAPI app with metadata and tags
app = FastAPI(
    title="Social Dashboard API",
    description="Backend for authentication, profiles, posts, engagements, analytics, and admin management.",
    version="1.0.0",
    openapi_tags=[
        {"name": "Health", "description": "Service health and info"},
        {"name": "Authentication", "description": "Register and login"},
        {"name": "Users", "description": "Users and profiles"},
        {"name": "Posts", "description": "Posts and engagements"},
        {"name": "Analytics", "description": "User and platform analytics"},
        {"name": "Admin", "description": "Administrative management"},
    ],
)

# Load settings and configure CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"], summary="Health Check")
def health_check():
    """Health check endpoint to verify the API is responsive."""
    return {"message": "Healthy"}


# PUBLIC_INTERFACE
@app.get("/websocket-usage", tags=["Health"], summary="WebSocket usage notes")
def websocket_usage():
    """Describe any real-time features (none implemented for now)."""
    return {
        "websocket": False,
        "note": "No WebSocket endpoints are currently implemented; future versions may add real-time updates.",
    }


# Include routers
app.include_router(routers_auth.router)
app.include_router(routers_users.router)
app.include_router(routers_posts.router)
app.include_router(routers_analytics.router)
app.include_router(routers_admin.router)
