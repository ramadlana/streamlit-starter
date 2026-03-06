# AGENTS.md

## 1) Mission
Use this file as the fast execution guide for this repo.

- App type: Flask auth gateway + Streamlit dashboard wrapper
- Primary DB: PostgreSQL only
- Auth/session: Flask-Login + Flask-WTF CSRF
- ORM: Flask-SQLAlchemy (`User`, `DocumentationPage`)
- SQL access pattern: ORM for core entities, raw SQL for feature/reporting helpers
- Python target: 3.10+

## 1.1) Delivery Mode (Spec-Driven)
Work in spec-first mode for any non-trivial change.

- Shared spec file: `SPECS.md`
- Rule: plan -> implement -> verify -> update spec evidence
- If scope changes, update `SPECS.md` first, then code

Minimum agent behavior:
1. Map request to an existing spec or create a new `SPEC-*` entry in `SPECS.md`.
2. Confirm files/routes/tables impacted before editing.
3. Implement only what is in scope for that spec.
4. Verify against spec acceptance criteria.
5. Record verification evidence in the spec change log/evidence section.

---

## 2) System Snapshot

### Runtime shape
- `run.py` starts **two processes**:
  - Flask app (`auth_server.py`) on `FLASK_PORT` (default `5001`)
  - Streamlit app (`dashboard_app.py`) on `STREAMLIT_PORT` (default `8501`)
- In `--prod` mode, Streamlit is served behind `/streamlit/` (Nginx proxies to it).
- Home route (`/`) is login-protected; `/iframe-app-streamlit` serves the page that embeds the Streamlit iframe (dev: localhost:8501, prod: `/streamlit/`).

### Core stack
- Flask 3.x
- Flask-Login
- Flask-WTF (`csrf` + per-form token)
- Flask-SQLAlchemy
- SQLAlchemy engine (`app_db/engine.py`) for raw SQL
- Streamlit multipage navigation (`dashboard_app.py`)

---

## 3) Repo Map (What lives where)

- `flask_app/`
  - `__init__.py`: app factory, extension setup, blueprint registration, CSRF error handling (import/register blueprints here)
  - `extensions.py`: extension instances (`login_manager`, `csrf`)
  - `routes/`: blueprints per feature
  - `routes/__init__.py`: package marker (required for `from flask_app.routes.<module> import bp`)
  - `routes/permissions.py`: decorators `role_required`, `admin_required` (not a blueprint)
  - `routes/auth.py`, `admin.py`, `home.py`, `docs.py`, `example_crud.py`, `dummydata_crud.py`, `iframe_app_streamlit.py`: blueprints
- `app_db/`
  - `__init__.py`: re-exports `db`, `User`, `DocumentationPage`, `get_sql_engine`, `build_database_uri`, role helpers, etc.
  - `base.py`: shared SQLAlchemy instance (`db`)
  - `config.py`: DB URI builder from env
  - `models.py`: ORM models (`User`, `DocumentationPage`)
  - `user_roles.py`: role constants/normalization + startup role-column ensure/backfill
  - `app_settings.py`: key-value app settings (e.g. `allow_signup`); admin-only writes
  - `docs.py`: docs query + persistence helpers
  - `docs_attachments.py`: docs attachment reference scan + orphan housekeeping helpers
  - `engine.py`: shared SQL engine for raw SQL features
  - `example_crud.py`: feature table bootstrap helper (no `dummydata.py`; that table is expected to exist)
- `templates/`: Jinja pages (extend `base.html`; no inline styles). Includes `base.html`, `home.html`, `login.html`, `signup.html`, `admin.html`, `docs_index.html`, `docs_view.html`, `docs_editor.html`, `example_crud.html`, `dummydata_crud.html`, `iframe_app_streamlit.html`, `change_password.html`, `components/modal.html`
- `static/css/`: `base.css` only (single stylesheet; see `FRAMEWORK_REFERENCE.md` Part II — Design System)
- `dashboard_pages/`: Streamlit page modules (e.g. `home.py`, `example/*.py`). Registered in `dashboard_app.py` via `st.Page(...)` and `st.navigation(...)`.
- `scripts/`: `manage_admin.py`, `kill_ports.py`, `docs_attachments_housekeeping.py`
- Root entrypoints:
  - `run.py`: starts Flask + Streamlit (use `--prod` for production)
  - `auth_server.py`: Flask app
  - `dashboard_app.py`: Streamlit multipage app

---

## 4) Read-First Order (Orientation path)
Read these in order when starting a task:

1. `flask_app/__init__.py`
2. `app_db/__init__.py`
3. `flask_app/routes/auth.py`
4. `flask_app/routes/admin.py`
5. `flask_app/routes/example_crud.py`
6. `flask_app/routes/dummydata_crud.py`
7. `flask_app/routes/docs.py`
8. `templates/base.html`
9. `run.py`
10. `FRAMEWORK_REFERENCE.md` (when adding or changing templates/CSS — Part II Design System, Part III § Base CSS)

---

## 5) Route & Blueprint Inventory

### Active blueprints
- `home`
- `auth`
- `admin`
- `example_crud`
- `dummydata_crud`
- `docs`
- `iframe_app_streamlit`

### Route groups (high-level)
- `home`
  - `/` (requires login)
- `auth`
  - `/login`
  - `/signup`
  - `/logout`
  - `/change-password`
  - `/auth-check`
- `admin`
  - `/admin`
  - `/admin/settings`
  - `/admin/add`
  - `/admin/edit/<user_id>`
  - `/admin/delete/<user_id>`
- `example_crud`
  - `/example-crud`
  - `/example-crud/create`
  - `/example-crud/edit/<item_id>`
  - `/example-crud/delete/<item_id>`
- `dummydata_crud`
  - `/dummydata-crud`
  - `/dummydata-crud/create`
  - `/dummydata-crud/edit/<item_id>`
  - `/dummydata-crud/delete/<item_id>`
- `docs`
  - `/docs`
  - `/docs/<slug>`
  - `/docs/tag/<tag>`
  - `/docs/editor/<doc_id>` (GET/POST)
  - `/docs/upload-image` (POST)
  - `/docs/attachments/<filename>`
  - `/docs/admin/attachments-housekeeping` (POST)
  - `/docs/admin/delete/<doc_id>` (POST)
- `iframe_app_streamlit`
  - `/iframe-app-streamlit` (protected; embeds Streamlit in iframe)

---

## 6) Environment Contract

Use either:
- `DATABASE_URL`

Or all of:
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`

Also:
- `SECRET_KEY`:
  - Required in production (`FLASK_DEBUG=False`)
  - Strongly recommended in development
- Optional runtime ports:
  - `FLASK_PORT` (default `5001`)
  - `STREAMLIT_PORT` (default `8501`)

### Non-negotiables
- Do not reintroduce SQLite configuration.
- Do not hardcode credentials or secrets.

---

## 7) Standard Commands

- Install deps:
  - `pip install -r requirements.txt`
- Run app (dev):
  - `python3 run.py`
- Run app (prod wiring):
  - `python3 run.py --prod`
- Create/promote admin:
  - `python3 scripts/manage_admin.py create <username> <email> <password>`
- List users:
  - `python3 scripts/manage_admin.py list`
- Free Flask/Streamlit ports (Linux/macOS):
  - `python3 scripts/kill_ports.py`
- Docs attachments housekeeping (dry-run default):
  - `python3 scripts/docs_attachments_housekeeping.py --include-legacy`
- Docs attachments housekeeping apply (move orphans to trash):
  - `python3 scripts/docs_attachments_housekeeping.py --apply --include-legacy`

---

## 8) Change Playbooks

### Add a protected Flask route
1. Add endpoint in `flask_app/routes/<feature>.py`.
2. Use `@login_required` for protected access.
3. Add template in `templates/<feature>/...` or reuse existing pages.
4. Use explicit `url_for("<blueprint>.<endpoint>")` in redirects/templates.
5. If new blueprint: **import** at top of `flask_app/__init__.py` (e.g. `from flask_app.routes.my_feature import bp as my_feature_bp`) and **register** inside `create_app()` with `app.register_blueprint(my_feature_bp)`.

### Add a CRUD feature
1. Create `flask_app/routes/<feature>.py` with a dedicated blueprint.
2. Put DB logic in `app_db/<feature>.py`.
3. ORM for core entities; raw SQL for reporting/complex queries.
4. Add template(s) in `templates/<feature>/...`.
5. Add nav link in `templates/base.html` if user-facing.

### Add a Streamlit page
1. Add module under `dashboard_pages/` (e.g. `dashboard_pages/my_page.py`). Include `import streamlit as st`.
2. In `dashboard_app.py`: add `my_page = st.Page("dashboard_pages/my_page.py", title="My Page", icon="...")` and add `my_page` to one of the lists in `st.navigation({...})`.
3. Keep business logic in `app_db`/Flask helpers, not in the Streamlit view.

---

## 9) ORM vs Raw SQL Decision Rule

Use ORM (`app_db/models.py`) when:
- Modeling core domain entities.
- Doing standard CRUD/filtering.
- Needing reusable model semantics.

Use raw SQL (`app_db/<feature>.py` + `engine.py`) when:
- Building reporting/analytics paths.
- Query shape is complex (joins/aggregations/windows).
- Table is feature-scoped and not worth full ORM model overhead.

Always:
- Source DB URI from `app_db/config.py` only.
- Keep heavy DB logic out of routes/templates.

---

## 10) Security & Template Rules

### Forms
Every HTML `POST` form must include:
```html
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
```

### Auth and authorization
- Login state is managed by Flask-Login session.
- Admin-only behavior is enforced by role-based checks (`role_required("admin", ...)`).
- Protect non-public pages with `@login_required`.

---

## 11) Compatibility & Refactor Guardrails

### Legacy compatibility files
- `models.py`
- `flask_app/models.py`

For new code, import from `app_db`.

### Safe refactor rules
- If renaming blueprints or endpoints, update **all** `url_for(...)` usages.
- Keep docs aligned when structure changes:
  - `README.md` (root)
  - `AGENTS.md`, `DEPLOYMENT.md`, `FRAMEWORK_REFERENCE.md` (in docs/)
- To remove all demo features (example/dummydata CRUD, docs, iframe-app-streamlit, Streamlit examples) and get a minimal framework, follow **`CLEAN_FRAMEWORK.md`** (in this folder).

---

## 12) Known Gotchas

- Streamlit proxy behavior differs by mode (`/streamlit/` in prod).
- Missing CSRF token in templates will break form submissions.
- `dummydata_crud` assumes `dummydata` table already exists.
- `db.create_all()` runs in app factory; avoid relying on it for non-ORM raw SQL tables.
- Docs uploads now write to `uploads/attachments/docs`; `/docs/attachments/<filename>` also falls back to legacy `uploads/attachments/changemanagement`.
- User roles are `viewer`, `editor`, `approval1`, `approval2`, `admin`; role is the single source for authorization checks.
- Sign up can be disabled by admin via **Admin Panel → Site settings** (“Allow new sign ups” toggle); when disabled, `/signup` redirects to login and the Sign Up nav link is hidden.

---

## 13) Done Checklist (before handing off)

Run:
```bash
python3 -m compileall -q app_db flask_app auth_server.py scripts models.py
```

Recommended if available:
- `pytest`

When changing templates/CSS, follow `FRAMEWORK_REFERENCE.md` (Design System & Base CSS):
- Single stylesheet (`base.css`); no new CSS files or inline `<style>` in templates
- Use standard classes (`btn`, `form-control`, `crud-panel-title`, etc.); no duplicate flash blocks

When changing docs/routing/features, verify:
- Route names + blueprint names match all `url_for(...)`
- Nav links still resolve
- Protected routes enforce login
- POST forms include CSRF token

Also verify against `SPECS.md`:
- Every delivered item maps to a `SPEC-*`.
- Acceptance criteria checkboxes are satisfied.
- Verification evidence is recorded before marking spec `Done`.
