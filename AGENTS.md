# AGENTS.md

## Goal
Fast orientation for AI agents working in this repository.

## Project Snapshot
- App type: Flask auth gateway + Streamlit dashboard wrapper
- Database: PostgreSQL
- Auth: Flask-Login
- ORM: Flask-SQLAlchemy (`User` model)
- Raw SQL usage: feature helpers via shared SQL engine
- Typical Python: 3.10+ (update if this changes)
- Typical stack: Flask 2.x, SQLAlchemy 1.4+/2.x, Streamlit (dashboard)

## Start Here (read in order)
1. `flask_app/__init__.py` (app factory + blueprint registration)
2. `app_db/__init__.py` (DB exports)
3. `flask_app/routes/auth.py` (auth flow)
4. `flask_app/routes/example_crud.py` (feature CRUD pattern)
5. `templates/base.html` (global nav/layout)
6. `run.py` (combined Flask + Streamlit runner)

## Folder Map
- `flask_app/routes/`: Flask blueprints (one file per feature)
- `app_db/`: DB layer
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

## Common Tasks Cheat Sheet

- **Add a new CRUD feature**
  - Create `flask_app/routes/<feature>.py` with a dedicated blueprint.
  - Put DB logic in `app_db/<feature>.py`:
    - Prefer ORM models in `app_db/models.py` for core entities.
    - Use raw SQL via `app_db/engine.py` for reporting/one-off or complex queries.
  - Add templates under `templates/<feature>/...` (views + forms, no business logic).
  - Add links/buttons to `templates/base.html` (global nav/layout).
  - Protect routes with `@login_required` if they require authentication.

- **Add a new protected route**
  - Add a view in the appropriate blueprint in `flask_app/routes/<feature>.py`.
  - Decorate with `@login_required` for any route that should only be used by logged-in users.
  - Use `url_for("<blueprint>.<endpoint>")` consistently in templates and redirects.

- **Add a new Streamlit page**
  - Create a module in `dashboard_pages/<page_name>.py`.
  - Follow existing patterns in that folder for how the page is registered/used.
  - Keep Streamlit pages focused on UI and calls into `app_db` helpers where needed.

## ORM vs Raw SQL: When to Use What

- **Use ORM (`app_db/models.py`) when:**
  - You are working with core domain entities (e.g. `User`, main business tables).
  - You want relationship management, migrations, or reusable models.
  - The queries are relatively straightforward (CRUD, filters, pagination).

- **Use raw SQL (`app_db/<feature>.py` + `engine.py`) when:**
  - You are implementing reporting/analytics or feature-specific queries.
  - The query is complex (aggregations, window functions, large joins) and easier to express in pure SQL.
  - You are working with temporary or auxiliary tables that don’t justify full ORM models.

- **Shared rules:**
  - Do not hardcode database URLs; always use configuration from `app_db/config.py`.
  - Keep heavy logic in `app_db`, not in route handlers or templates.

## Auth Flow Overview

- **Stack:** Flask-Login with a `User` model defined in `app_db/models.py`.
- **Where to look:**
  - `flask_app/__init__.py`: Flask app factory and `LoginManager` setup.
  - `flask_app/routes/auth.py`: login, signup, logout, auth-check endpoints.
- **How authentication works (high-level):**
  - Users log in via `/login` (form posts credentials, `User` is loaded from Postgres).
  - Flask-Login manages the session; `@login_required` gates protected views (including `/`).
  - Logout clears the session; `/auth-check` can be used by clients to verify if a user is authenticated.
- **Authorization / roles:**
  - Admin-related behavior is handled via the `admin` blueprint (`flask_app/routes/admin.py`); check that file for any role/permission logic.

## Required Environment
Use either:
- `DATABASE_URL`

Or all of:
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `SECRET_KEY` (required in production mode; recommended always)

### Environment Do/Don't

- **Do:**
  - Configure the database via `DATABASE_URL` or the `DB_*` variables only.
  - Set `SECRET_KEY` in all environments (dev/prod) to keep sessions secure.
  - Keep any `.env` or secret files out of version control.

- **Don't:**
  - Hardcode credentials, connection strings, or secret keys in Python or templates.
  - Reintroduce SQLite configuration anywhere (this app is Postgres-only going forward).

## Current Blueprints
- `home`: `/` (protected)
- `auth`: `/login`, `/signup`, `/logout`, `/auth-check`
- `admin`: `/admin` + user management endpoints
- `example_crud`: `/example-crud` + CRUD endpoints

### Route / URL Map (High Level)

- **`home` blueprint**
  - `/` – main authenticated landing page / dashboard wrapper.

- **`auth` blueprint**
  - `/login` – login form + POST handler.
  - `/signup` – new user registration (if enabled).
  - `/logout` – logout and redirect.
  - `/auth-check` – simple endpoint to check authentication status.

- **`admin` blueprint**
  - `/admin` – admin home (often user list or admin dashboard).
  - Additional admin/user management endpoints live in `flask_app/routes/admin.py`.

- **`example_crud` blueprint**
  - `/example-crud` – list/create/update/delete following the example CRUD pattern.

## Coding Conventions
- Keep each new feature in a dedicated route file (`flask_app/routes/<feature>.py`)
- Keep SQL/helper logic in `app_db/<feature>.py` when using raw SQL
- Keep templates dumb: rendering + forms only, no business logic
- Use `@login_required` for protected routes
- Use explicit endpoint names in `url_for("blueprint.endpoint")`
- For every HTML `<form method="POST">`, include CSRF hidden input:
  - `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">`

## Compatibility Notes
- Legacy compatibility shims exist:
  - `models.py`
  - `flask_app/models.py`
- Prefer imports from `app_db` for new code.

## Safe Refactor Rules
- Do not re-introduce SQLite config
- Do not rename routes or blueprints without updating all `url_for(...)` references
- Keep docs in sync when changing structure:
  - `README.md`
  - `AGENTS.md`

## Known Gotchas

- `models.py` and `flask_app/models.py` exist mostly for legacy compatibility; new code should import models from `app_db.models`.
- Changing blueprint names or endpoint names without updating all `url_for(...)` uses in templates and Python will break navigation.
- Streamlit integration is coordinated via `run.py`; avoid putting heavy business logic directly in Streamlit code—delegate to `app_db` or Flask routes.
- Forms must include the CSRF hidden input to avoid CSRF protection errors.

## Validation Before Finishing
Run:
```bash
python3 -m compileall -q app_db flask_app auth_server.py scripts models.py
```

If tests or additional validation commands are added later (e.g. `pytest`), prefer running them as part of your workflow and document them here.
