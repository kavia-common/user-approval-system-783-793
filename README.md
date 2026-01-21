# user-approval-system-783-793 (api_backend)

FastAPI backend for the Social Dashboard.

## Quickstart

1) Ensure the database is initialized:
   - Navigate to user-approval-system-783-794/main_database
   - Run: python3 migrate_and_seed.py
   - Note the absolute path to myapp.db in db_connection.txt

2) Configure environment:
   - Copy api_backend/.env.example to api_backend/.env
   - Set:
     DB_PATH=<absolute path to myapp.db>
     JWT_SECRET=<strong secret>
     PORT=3001

3) Install and run:
   cd api_backend
   pip install -r requirements.txt
   uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-3001} --reload

OpenAPI: http://localhost:3001/docs
Health:   http://localhost:3001/

See api_backend/README.md for details.
