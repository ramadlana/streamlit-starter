# Streamlit Gatekeeper

Flask authentication gateway for Streamlit, with PostgreSQL-backed users and CRUD feature patterns.

---

## What This Starter Does

- **Protect Streamlit** behind Flask login/session (dashboard only after auth).
- **User management** in PostgreSQL with roles (viewer, editor, approval1, approval2, admin).
- **Admin panel** for users and site settings (e.g. disable sign-up).
- **Templates** for protected Flask pages and Streamlit dashboard pages.

---

## Architecture at a Glance

`run.py` starts two processes:

| Process    | Port (default) | Role                          |
|-----------|----------------|-------------------------------|
| **Flask** | 5001           | Auth gateway, HTML pages, API |
| **Streamlit** | 8501        | Dashboards (iframe from Flask) |

In production (`run.py --prod`), Streamlit is served under `/streamlit/` behind Nginx.

**Stack:** Flask, Flask-Login, Flask-WTF CSRF, Flask-SQLAlchemy, PostgreSQL (`psycopg2`), Streamlit.

---

## Quick Start (Development)

Use this flow on **Windows**, **Linux**, or **macOS** to run the app locally.

### 1. Clone and enter the project

```bash
git clone https://github.com/ramadlana/streamlit-starter
cd streamlit-starter
```

### 2. Create a virtual environment

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (Command Prompt):**

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set environment variables

**Option A — Individual DB variables**

Linux/macOS:

```bash
export DB_USER=appuser
export DB_PASSWORD=strongpassword
export DB_HOST=127.0.0.1
export DB_PORT=5432
export DB_NAME=appdb
export SECRET_KEY=change-this-secret-key-in-dev
export FLASK_PORT=5001
export STREAMLIT_PORT=8501
```

Windows (CMD): use `set VAR=value` for each. Windows (PowerShell): use `$env:VAR="value"` for each.

**Option B — Single `DATABASE_URL` (any OS):**

```bash
export DATABASE_URL=postgresql+psycopg2://appuser:strongpassword@127.0.0.1:5432/appdb
export SECRET_KEY=change-this-secret-key-in-dev
export FLASK_PORT=5001
export STREAMLIT_PORT=8501
```

### 5. Start PostgreSQL

Ensure PostgreSQL is running and the database exists.

**Docker (all platforms):**

```bash
docker run -d \
  --name postgres-appdb \
  -p 5432:5432 \
  -e POSTGRES_USER=appuser \
  -e POSTGRES_PASSWORD=strongpassword \
  -e POSTGRES_DB=appdb \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:16
```

**Linux:** use your distro’s PostgreSQL package. **macOS:** `brew services start postgresql@16`. **Windows:** install from the official PostgreSQL installer and create the database.

Optional — create the `dummydata` table if you use that feature:

```sql
CREATE TABLE public.dummydata (
  id serial NOT NULL PRIMARY KEY,
  name text NOT NULL,
  email text NOT NULL,
  created_at timestamp without time zone NULL DEFAULT now()
);
```

### 6. Create the first admin user

```bash
python3 scripts/manage_admin.py create admin admin@example.com admin123
```

On Windows use `python` if that’s how Python is on your PATH.

### 7. Run the app

```bash
python3 run.py
```

- **Flask:** http://localhost:5001 (or your `FLASK_PORT`)
- **Streamlit:** reached from the Flask home page after login (iframe to port 8501 by default)

**Ports in use:** On Linux/macOS, `run.py` tries to free the ports first; you can also run `python3 scripts/kill_ports.py`. On Windows, `lsof` is not available — stop the process using the port (Task Manager or `taskkill`) or use different `FLASK_PORT` / `STREAMLIT_PORT`.

### Development checklist

| Step | Action |
|------|--------|
| 1 | Clone repo, `cd` into project |
| 2 | Create venv and activate it |
| 3 | `pip install -r requirements.txt` |
| 4 | Set `DATABASE_URL` or `DB_*` + `SECRET_KEY` (+ optional ports) |
| 5 | Start PostgreSQL and create DB (and optional `dummydata` table) |
| 6 | `python3 scripts/manage_admin.py create admin admin@example.com <password>` |
| 7 | `python3 run.py` → open http://localhost:5001 |

**Production (server) deployment:** see **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)**.

---

## Environment Variables

- **Database:** `DATABASE_URL` **or** `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`.
- **Required in production:** `SECRET_KEY`.
- **Optional:** `FLASK_PORT` (default `5001`), `STREAMLIT_PORT` (default `8501`).

PostgreSQL only; no SQLite. Do not hardcode credentials. Production env and full variable table: **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md#3-environment-variables-reference)**.

---

## Project Layout

```
run.py              # Starts Flask + Streamlit
auth_server.py      # Flask entrypoint
dashboard_app.py   # Streamlit entrypoint
flask_app/         # App factory, blueprints (routes/)
app_db/            # DB config, models, engine, helpers
templates/         # Jinja HTML (extend base.html)
static/css/        # base.css only
dashboard_pages/   # Streamlit pages
scripts/           # manage_admin, kill_ports, docs_attachments_housekeeping
```

Detailed repo map and read-first order: **[docs/AGENTS.md](docs/AGENTS.md)**.

---

## Routes (Summary)

- **Auth:** `/login`, `/signup`, `/logout`, `/change-password`, `/auth-check`
- **Home:** `/` (protected; shows Streamlit iframe)
- **Admin:** `/admin`, `/admin/settings` (admin only)
- **CRUD examples:** `/example-crud`, `/dummydata-crud`
- **Docs:** `/docs`, `/docs/<slug>`, `/docs/editor/<id>`, etc.
- **Streamlit iframe:** `/iframe-app-streamlit`

Full route list, blueprints, and how to protect or restrict by role: **[docs/FRAMEWORK_REFERENCE.md](docs/FRAMEWORK_REFERENCE.md)**.

---

## Database Notes

- **User** and **documentation_pages** are ORM-managed; `db.create_all()` runs at startup.
- **Roles:** viewer, editor, approval1, approval2, admin; role column is ensured at startup.
- **app_settings:** key-value (e.g. allow_signup); created at startup.
- **example_crud_items** is created by a startup helper.
- **dummydata** table must exist if you use that feature; DDL is in the [Quick Start](#quick-start-development) above.

---

## Common Commands

| Command | Purpose |
|--------|---------|
| `python3 run.py` | Run app (development) |
| `python3 run.py --prod` | Run with production wiring (expects Nginx) |
| `python3 scripts/manage_admin.py create <user> <email> <pass>` | Create/promote admin |
| `python3 scripts/manage_admin.py list` | List users |
| `python3 scripts/kill_ports.py` | Free Flask/Streamlit ports (Linux/macOS) |
| `python3 scripts/docs_attachments_housekeeping.py --include-legacy` | Docs attachments dry-run |
| `python3 -m compileall -q app_db flask_app auth_server.py scripts` | Syntax check |

---

## Documentation (Where to Go for More)

| Document | Purpose |
|----------|---------|
| **[docs/PROMPTING_GUIDE.md](docs/PROMPTING_GUIDE.md)** | Prompt templates and placeholders for adding new features (follow AGENTS.md). |
| **[docs/CLEAN_FRAMEWORK.md](docs/CLEAN_FRAMEWORK.md)** | Remove all demo features (example/dummydata CRUD, docs, iframe-app-streamlit, Streamlit example pages) for a minimal framework. |
| **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** | **Production only:** server setup, systemd, Nginx, env file, troubleshooting. |
| **[docs/FRAMEWORK_REFERENCE.md](docs/FRAMEWORK_REFERENCE.md)** | Architecture diagrams, design system (HTML/CSS), and user guide: auth, roles, protecting pages, adding Flask/Streamlit pages, CSRF, nav by role, CRUD pattern, DB patterns, CSS reference. |
| **[docs/AGENTS.md](docs/AGENTS.md)** | Repo map, route/blueprint inventory, playbooks (add route, CRUD, Streamlit page), security rules, for contributors and automation. |
| **[docs/SPECS.md](docs/SPECS.md)** | Spec-driven workflow for non-trivial changes; template and status. |

---

## Troubleshooting (development)

- **Missing PostgreSQL configuration** — Set `DATABASE_URL` or all `DB_*` vars; ensure the database and user exist.
- **Port in use** — On Linux/macOS run `python3 scripts/kill_ports.py`. On Windows, stop the process using the port or set different `FLASK_PORT` / `STREAMLIT_PORT`.
- **Session / CSRF issues** — Use a stable `SECRET_KEY`; every POST form needs the CSRF token (see [docs/FRAMEWORK_REFERENCE.md](docs/FRAMEWORK_REFERENCE.md)).
- **404 or BuildError** — Check blueprint registration in `flask_app/__init__.py` and `url_for("blueprint.endpoint")` names. See [docs/FRAMEWORK_REFERENCE.md](docs/FRAMEWORK_REFERENCE.md#common-mistakes-when-adding-pages) (common mistakes).

Production issues: **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md#4-troubleshooting)**.

---

## Roadmap

- Docs workflow: approval lifecycle and audit history by role.
- Production hardening: search/filter, pagination, notifications, optional object storage.
- Tests for docs role permissions and attachment housekeeping.
