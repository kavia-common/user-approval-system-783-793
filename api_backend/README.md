# Social Dashboard API (FastAPI)

Handles authentication, user/profile management, posts & engagements, analytics, and admin features.

## Prerequisites
- Python 3.11+
- The SQLite database built by the main_database container (myapp.db)

## Environment
Copy `.env.example` to `.env` and set:

- DB_PATH: absolute path to the SQLite db file produced by main_database.
  Example: /tmp/kavia/workspace/code-generation/user-approval-system-783-794/main_database/myapp.db
- JWT_SECRET: a strong secret string
- PORT: default 3001

Optional:
- CORS_ALLOW_ORIGINS (defaults to *)
- ACCESS_TOKEN_EXPIRE_MINUTES

## Install
pip install -r requirements.txt

## Run
- Development:
  uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-3001} --reload

The app reads configuration from environment variables (.env will be loaded by the orchestrator/environment). Ensure DB_PATH points to the myapp.db created by the database container.

## Health
GET /

## Core Endpoints
- POST /auth/register
- POST /auth/login
- GET /users/me, PUT /users/me/profile, GET /users/me/profile
- POST /posts, GET /posts/me, POST /posts/{id}/engagements
- GET /analytics/me (per-user), GET /analytics/platform (admin)
- Admin: DELETE /admin/posts/{id}, DELETE /admin/users/{id}, GET /users (admin), PUT /users/{id}/activate, PUT /users/{id}/role

## Notes
- Uses simple HMAC-based JWT implementation in src/api/security.py (no external JWT lib).
- Requires myapp.db schema from main_database to match the expected tables.
