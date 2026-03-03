# AGENTS.md

## Goal
Fast orientation for AI agents working in this repository.

## Project Snapshot
- App type: Flask auth gateway + Streamlit dashboard wrapper
- Database: PostgreSQL
- Auth: Flask-Login
- ORM: Flask-SQLAlchemy (`User` model)
- Raw SQL usage: feature helpers via shared SQL engine

## Start Here (read in order)
1. `flask_app/__init__.py` (app factory + blueprint registration)
2. `flask_app/db/__init__.py` (DB exports)
3. `flask_app/routes/auth.py` (auth flow)
4. `flask_app/routes/example_crud.py` (feature CRUD pattern)
5. `templates/base.html` (global nav/layout)
6. `run.py` (combined Flask + Streamlit runner)

## Folder Map
- `flask_app/routes/`: Flask blueprints (one file per feature)
- `flask_app/db/`: DB layer
  - `base.py`: SQLAlchemy instance
  - `config.py`: DB URL builder
  - `engine.py`: shared SQL engine for raw SQL features
  - `models.py`: ORM models (`User`)
  - `example_crud.py`: helper for example CRUD table bootstrap
- `templates/`: Jinja templates
- `dashboard_pages/`: Streamlit pages
- `scripts/`: CLI utilities

## Runtime and Commands
- Install: `pip install -r requirements.txt`
- Run dev: `python3 run.py`
- Run prod mode: `python3 run.py --prod`
- Create admin: `python3 scripts/manage_admin.py create <username> <email> <password>`
- List users: `python3 scripts/manage_admin.py list`

## Required Environment
Use either:
- `DATABASE_URL`

Or all of:
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`

## Current Blueprints
- `home`: `/` (protected)
- `auth`: `/login`, `/signup`, `/logout`, `/auth-check`
- `admin`: `/admin` + user management endpoints
- `example_crud`: `/example-crud` + CRUD endpoints

## Coding Conventions
- Keep each new feature in a dedicated route file (`flask_app/routes/<feature>.py`)
- Keep SQL/helper logic in `flask_app/db/<feature>.py` when using raw SQL
- Keep templates dumb: rendering + forms only, no business logic
- Use `@login_required` for protected routes
- Use explicit endpoint names in `url_for("blueprint.endpoint")`

## Compatibility Notes
- Legacy compatibility shims exist:
  - `models.py`
  - `flask_app/models.py`
- Prefer imports from `flask_app.db` for new code.

## Safe Refactor Rules
- Do not re-introduce SQLite config
- Do not rename routes or blueprints without updating all `url_for(...)` references
- Keep docs in sync when changing structure:
  - `README.md`
  - `USER_GUIDE.md`
  - `AGENTS.md`

## Validation Before Finishing
Run:
```bash
python3 -m compileall -q flask_app auth_server.py scripts
```
