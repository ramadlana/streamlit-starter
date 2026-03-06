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
- In `--prod` mode, Streamlit is served behind `/dashboard-app/`.
- Home route (`/`) is login-protected and renders Streamlit URL into the template.

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
  - `__init__.py`: app factory, extension setup, blueprint registration, CSRF error handling
  - `extensions.py`: extension instances (`login_manager`, `csrf`)
  - `routes/`: blueprints per feature
- `app_db/`
  - `base.py`: shared SQLAlchemy instance (`db`)
  - `config.py`: DB URI builder from env
  - `models.py`: ORM models (`User`, `DocumentationPage`)
  - `user_roles.py`: role constants/normalization + startup role-column ensure/backfill
  - `app_settings.py`: key-value app settings (e.g. `allow_signup`); admin-only writes
  - `docs.py`: docs query + persistence helpers
  - `docs_attachments.py`: docs attachment reference scan + orphan housekeeping helpers
  - `engine.py`: shared SQL engine for raw SQL features
  - `example_crud.py`: feature table bootstrap helper
- `templates/`: Jinja pages and forms (extend `base.html`; no inline styles)
- `static/css/`: `base.css` only (single stylesheet; see `DESIGN_SYSTEM.md`)
- `DESIGN_SYSTEM.md`: HTML/CSS standards and component reference for the starter kit
- `dashboard_pages/`: Streamlit pages
- `scripts/`: operational utilities (`manage_admin.py`, `docs_attachments_housekeeping.py`, etc.)
- Root entrypoints:
  - `run.py`
  - `auth_server.py`
  - `dashboard_app.py`

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
10. `DESIGN_SYSTEM.md` (when adding or changing templates/CSS)

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
  - `/docs/editor/<id>`
  - `/docs/tag/<tag>`
  - `/docs/upload-image`
  - `/docs/attachments/<filename>`
  - `/docs/admin/attachments-housekeeping`
  - `/docs/admin/delete/<id>`
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
5. Register blueprint in `flask_app/__init__.py` if new.

### Add a CRUD feature
1. Create `flask_app/routes/<feature>.py` with a dedicated blueprint.
2. Put DB logic in `app_db/<feature>.py`.
3. ORM for core entities; raw SQL for reporting/complex queries.
4. Add template(s) in `templates/<feature>/...`.
5. Add nav link in `templates/base.html` if user-facing.

### Add a Streamlit page
1. Add module under `dashboard_pages/`.
2. Register it in `dashboard_app.py` via `st.Page(...)` and navigation group.
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
  - `README.md`
  - `AGENTS.md`

---

## 12) Known Gotchas

- Streamlit proxy behavior differs by mode (`/dashboard-app/` in prod).
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

When changing templates/CSS, follow `DESIGN_SYSTEM.md`:
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
