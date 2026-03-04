# Streamlit Gatekeeper

Flask authentication gateway for Streamlit, with PostgreSQL-backed users and CRUD feature patterns.

## 1) What This Starter Solves
- Protect Streamlit behind Flask login/session.
- Keep auth and user management in PostgreSQL.
- Provide admin user management endpoints.
- Provide feature templates for protected CRUD pages.

## 2) Architecture At A Glance

### Runtime model
`run.py` launches:
- Flask app (`auth_server.py`) on `FLASK_PORT` (default `5001`)
- Streamlit app (`dashboard_app.py`) on `STREAMLIT_PORT` (default `8501`)

In `--prod` mode, Streamlit is served behind `/dashboard-app/` and typically fronted by Nginx.

### Core stack
- Flask, Flask-Login, Flask-WTF CSRF
- Flask-SQLAlchemy + SQLAlchemy engine
- PostgreSQL (`psycopg2`)
- Streamlit multipage app

## 3) Quick Start (Development)

### 3.1 Clone and install
```bash
git clone https://github.com/ramadlana/streamlit-starter
cd streamlit-starter
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3.2 Start PostgreSQL
Use your preferred setup (Docker/local service). Example Docker:
```bash
docker run -d \
  --name postgres-appdb \
  --restart unless-stopped \
  -p 5432:5432 \
  -e POSTGRES_USER=appuser \
  -e POSTGRES_PASSWORD=strongpassword \
  -e POSTGRES_DB=appdb \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:16
```

### 3.3 Configure environment
Use either `DATABASE_URL` or full `DB_*` variables.

Option A (`DB_*`):
```bash
export DB_USER=appuser
export DB_PASSWORD=strongpassword
export DB_HOST=127.0.0.1
export DB_PORT=5432
export DB_NAME=appdb
export SECRET_KEY=change-this-secret
export FLASK_PORT=5001
export STREAMLIT_PORT=8501
```

Option B (`DATABASE_URL`):
```bash
export DATABASE_URL=postgresql+psycopg2://appuser:strongpassword@127.0.0.1:5432/appdb
export SECRET_KEY=change-this-secret
export FLASK_PORT=5001
export STREAMLIT_PORT=8501
```

### 3.4 Create first admin
```bash
python3 scripts/manage_admin.py create admin admin@example.com admin123
```

### 3.5 Run app
```bash
python3 run.py
```

Access:
- Flask UI: `http://127.0.0.1:5001`
- Streamlit is accessed from protected Flask home after login

## 4) Environment Contract
Required DB config:
- `DATABASE_URL`
- or `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`

Security/runtime:
- `SECRET_KEY` (required in production; strongly recommended always)
- `FLASK_PORT` (optional, default `5001`)
- `STREAMLIT_PORT` (optional, default `8501`)

Rules:
- PostgreSQL only (no SQLite fallback).
- Do not hardcode credentials/secrets.

## 5) Routes and Access Model

### Blueprints
- `home`
- `auth`
- `admin`
- `example_crud`
- `dummydata_crud`

### Core routes
- `/login`
- `/signup`
- `/logout`
- `/auth-check`
- `/` (protected)
- `/admin` (admin-only)
- `/example-crud` (protected)
- `/dummydata-crud` (protected)

## 6) Project Layout
```text
.
├── run.py
├── auth_server.py
├── dashboard_app.py
├── flask_app/
│   ├── __init__.py
│   ├── extensions.py
│   └── routes/
│       ├── auth.py
│       ├── home.py
│       ├── admin.py
│       ├── example_crud.py
│       └── dummydata_crud.py
├── app_db/
│   ├── base.py
│   ├── config.py
│   ├── engine.py
│   ├── models.py
│   └── example_crud.py
├── templates/
├── dashboard_pages/
└── scripts/
```

## 7) Database Notes
- `User` table is managed through SQLAlchemy (`db.create_all()` in app factory).
- `example_crud_items` is auto-created by `ensure_example_crud_table()`.
- `dummydata` table is expected to exist already.

Example DDL for `dummydata`:
```sql
CREATE TABLE public.dummydata (
  id serial NOT NULL,
  name text NOT NULL,
  email text NOT NULL,
  created_at timestamp without time zone NULL DEFAULT now(),
  CONSTRAINT dummydata_pkey PRIMARY KEY (id)
);
```

## 8) Development Playbooks

Before non-trivial implementation work, define/refine a spec in `SPECS.md` and execute against its acceptance criteria.

### Add a protected Flask feature
1. Create `flask_app/routes/<feature>.py` blueprint.
2. Add endpoints and protect with `@login_required` as needed.
3. Add templates under `templates/`.
4. Register blueprint in `flask_app/__init__.py`.
5. Add navigation link in `templates/base.html` if user-facing.

### Add a new CRUD page
1. Put DB logic in `app_db/<feature>.py`.
2. Use raw SQL via `get_sql_engine()` for feature/reporting tables.
3. Keep route handlers thin (validate input, call DB helpers, render/redirect).

### Add a Streamlit page
1. Add file under `dashboard_pages/`.
2. Register with `st.Page(...)` in `dashboard_app.py`.
3. Keep heavy logic out of page files.

## 9) Security Checklist
- Include CSRF token on every HTML `POST` form:
```html
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
```
- Use `@login_required` for protected routes.
- Keep admin checks in route logic (`admin_required`).
- Set stable `SECRET_KEY` across restarts.

## 10) Production (systemd + Nginx)

### 10.1 Example systemd unit
`/etc/systemd/system/streamgatekeeper.service`
```ini
[Unit]
Description=Streamlit Gatekeeper (Flask + Streamlit)
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/streamgatekeeper
EnvironmentFile=/etc/streamgatekeeper/streamgatekeeper.env
ExecStart=/opt/streamgatekeeper/.venv/bin/python3 /opt/streamgatekeeper/run.py --prod
Restart=always
RestartSec=5
KillMode=control-group
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
```

### 10.2 Example env file
`/etc/streamgatekeeper/streamgatekeeper.env`
```bash
DATABASE_URL=postgresql+psycopg2://appuser:strongpassword@127.0.0.1:5432/appdb
SECRET_KEY=replace-with-a-long-random-secret
FLASK_PORT=5001
STREAMLIT_PORT=8501
```

Secure it:
```bash
sudo chown root:root /etc/streamgatekeeper/streamgatekeeper.env
sudo chmod 600 /etc/streamgatekeeper/streamgatekeeper.env
```

### 10.3 Example Nginx site
```nginx
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location = /auth-check {
        internal;
        proxy_pass http://127.0.0.1:5001/auth-check;
        proxy_pass_request_body off;
        proxy_set_header Content-Length "";
    }

    location /dashboard-app/ {
        auth_request /auth-check;
        proxy_pass http://127.0.0.1:8501/dashboard-app/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## 11) Common Commands
- Run app: `python3 run.py`
- Run production wiring: `python3 run.py --prod`
- List users: `python3 scripts/manage_admin.py list`
- Create/promote admin: `python3 scripts/manage_admin.py create <username> <email> <password>`
- Cleanup occupied ports: `python3 scripts/kill_ports.py`
- Validation compile: `python3 -m compileall -q app_db flask_app auth_server.py scripts models.py`

## 12) Troubleshooting
- `Missing PostgreSQL configuration`:
  - Set `DATABASE_URL` or all `DB_*` vars.
- Session resets unexpectedly:
  - Ensure `SECRET_KEY` is set and stable.
- Production boot error:
  - `SECRET_KEY` is mandatory when debug is off.
- `BuildError` from templates:
  - Check `url_for("blueprint.endpoint")` names.
- 404 on route:
  - Ensure blueprint is registered in `flask_app/__init__.py`.
- CSRF/session-expired message on submit:
  - Reload the page and resubmit.

## 13) Agent Context
- [AGENTS.md](AGENTS.md)
- [SPECS.md](SPECS.md)

## 14) Roadmap (Condensed)
- Add documentation module (editor + slug/tag pages + attachment support).
- Add change-management workflow (multi-step approvals + audit history).
- Add production hardening (search/filter, pagination, notifications, optional object storage).
