import streamlit as st

st.markdown(
    """
# Streamlit Gatekeeper

Flask authentication wrapper for Streamlit apps with PostgreSQL-backed auth/users and example CRUD.

## Why this starter
- Secure Streamlit behind Flask login
- PostgreSQL for auth + app data
- Admin panel for user management
- Simple project layout for adding new features quickly

## Tech stack
- Flask, Flask-Login, Flask-SQLAlchemy
- SQLAlchemy + psycopg2 (PostgreSQL)
- Streamlit multi-page app

## Quick Run (development)

### 1. Create virtualenv and install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate  # adjust if your venv path/name differs
pip install -r requirements.txt
```

### 2. Configure database and app environment

Linux/Mac:

```bash
export DB_USER=appuser
export DB_PASSWORD=strongpassword
export DB_HOST=127.0.0.1
export DB_PORT=5432
export DB_NAME=appdb
export SECRET_KEY=change-this-internal-secret
export FLASK_PORT=5001
export STREAMLIT_PORT=8501
```

Windows (cmd):

```bat
set DB_USER=appuser
set DB_PASSWORD=strongpassword
set DB_HOST=127.0.0.1
set DB_PORT=5432
set DB_NAME=appdb
set SECRET_KEY=change-this-internal-secret
set FLASK_PORT=5001
set STREAMLIT_PORT=8501
```

Alternative (single URL):

```bash
export DATABASE_URL=postgresql+psycopg2://appuser:strongpassword@127.0.0.1:5432/appdb
export SECRET_KEY=change-this-internal-secret
export FLASK_PORT=5001
export STREAMLIT_PORT=8501
```

create dummydata table:
```sql
CREATE TABLE public.dummydata (
  id serial NOT NULL,
  name text NOT NULL,
  email text NOT NULL,
  created_at timestamp without time zone NULL DEFAULT now()
);

ALTER TABLE public.dummydata
ADD CONSTRAINT dummydata_pkey PRIMARY KEY (id);
```

### 3. Create first admin user

```bash
python3 scripts/manage_admin.py create admin admin@example.com admin123
```

### 4. Run the app in development mode

```bash
python3 run.py
```

- Flask UI: `http://127.0.0.1:5001`
- Streamlit dashboard is proxied behind Flask after login

## Core URLs
- `/login` - sign in
- `/signup` - register user
- `/` - protected home
- `/example-crud` - protected CRUD example
- `/admin` - admin-only user management

## Project Structure
```text
.
├── auth_server.py
├── dashboard_app.py
├── run.py
├── flask_app/
│   ├── __init__.py            # app factory + blueprint registration
│   ├── extensions.py          # login_manager
│   ├── routes/
│   │   ├── auth.py
│   │   ├── home.py
│   │   ├── admin.py
│   │   └── example_crud.py
├── app_db/
│   ├── __init__.py
│   ├── base.py                # db = SQLAlchemy()
│   ├── config.py              # DB URI builder
│   ├── engine.py              # shared SQL engine (raw SQL helpers)
│   ├── models.py              # ORM User model
│   └── example_crud.py        # example feature table bootstrap helper
├── templates/
├── dashboard_pages/
└── scripts/
```

## Developer Workflow

### Example vs real tables

- **Auth / `User` model**: created automatically by SQLAlchemy on startup via `db.create_all()`; you do not need to create this table manually.
- **Example CRUD table**: the `/example-crud` feature uses a demo table named `example_crud_items`, which is auto-created if missing by `app_db/example_crud.py` (`ensure_example_crud_table()`).
- **Real feature tables**: for your own features (for example, a `dummydata` table), you are expected to create/manage tables via migrations or SQL, and have routes issue straightforward `SELECT/INSERT/UPDATE/DELETE` queries against them. There is no need to auto-create real tables in request handlers.

### Add a public/protected page

Use this pattern:
1. Create `flask_app/routes/<feature>.py` with a blueprint.
2. Add public/protected routes (`@login_required` for protected).
3. Register the blueprint in `flask_app/__init__.py`.
4. Add matching templates in `templates/`.
5. Use explicit `url_for("blueprint.endpoint")` names.

### (Optional) Using AI agents to scaffold a new CRUD

If you are using Cursor or another AI-powered editor, you can paste and adapt this prompt to quickly generate a new CRUD feature:

> You are working in my `streamlit-starter` repo (Flask auth gateway + Streamlit dashboard). Follow `AGENTS.md` and this `README.md`. I want you to generate a new protected CRUD feature in the same style as `example_crud`, but backed by the table defined below (PostgreSQL).
>
> 1. Read `flask_app/routes/example_crud.py`, `app_db/example_crud.py`, `templates/example_crud.html`, `templates/base.html`, `flask_app/__init__.py`, and `app_db/__init__.py` to mirror patterns and conventions.
> 2. Create a new CRUD blueprint under `flask_app/routes/<feature>_crud.py` that:
>    - Uses `@login_required` on all routes.
>    - Uses `get_sql_engine()` and raw SQL for `SELECT/INSERT/UPDATE/DELETE` on my table (do not auto-create the table).
> 3. Create a new template `templates/<feature>_crud.html`:
>    - Extend `base.html`.
>    - Include `form_and_table.css` like `example_crud.html`.
>    - Show a table listing all rows with sensible columns.
>    - Provide a right-hand form to create/update rows, with JS like `example_crud.html` to toggle “New” vs “Edit”.
> 4. Wire it up:
>    - Register the new blueprint in `flask_app/__init__.py`.
>    - Add a nav link in `templates/base.html` under the authenticated user section.
> 5. Update docs:
>    - Append a short section to `README.md` under “Developer Workflow” describing this new CRUD feature and including the table DDL.
> 6. Ensure everything compiles (run `python3 -m compileall -q app_db flask_app auth_server.py scripts models.py`) and fix any simple errors.
>
> **Table DDL (Data Definition Languange) to use (edit this block as needed):**
>
> ```sql
> CREATE TABLE public.dummydata (
>   id serial NOT NULL,
>   name text NOT NULL,
>   email text NOT NULL,
>   created_at timestamp without time zone NULL DEFAULT now()
> );
>
> ALTER TABLE public.dummydata
> ADD CONSTRAINT dummydata_pkey PRIMARY KEY (id);
> ```

#### Example: `dummydata` table DDL

For the `dummydata` CRUD example, you can create the backing table on a new database with:

```sql
CREATE TABLE public.dummydata (
  id serial NOT NULL,
  name text NOT NULL,
  email text NOT NULL,
  created_at timestamp without time zone NULL DEFAULT now()
);

ALTER TABLE public.dummydata
ADD CONSTRAINT dummydata_pkey PRIMARY KEY (id);
```

## Production Run (Linux with systemd + Nginx)

Use this when deploying to a server (e.g. Ubuntu) under `/opt`, managed by `systemd` and fronted by Nginx.

Use this structure:
- App path: `/opt/myappname`
- Env file: `/etc/myappname/myapp.env`
- Service file: `/etc/systemd/system/myappname.service`

1. Server setup:
```bash
sudo apt update
sudo apt install -y python3-pip python3-venv nginx
sudo mkdir -p /opt/myappname /etc/myappname
sudo chown -R $USER:$USER /opt/myappname
```

2. Copy project and install:
```bash
cd /opt/myappname
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Create env file:
```bash
sudo nano /etc/myappname/myapp.env
```

Example content:
```bash
DATABASE_URL=postgresql+psycopg2://appuser:strongpassword@127.0.0.1:5432/appdb
SECRET_KEY=replace-with-a-long-random-secret
FLASK_PORT=5001
STREAMLIT_PORT=8501
```

Secure it:
```bash
sudo chown root:root /etc/myappname/myapp.env
sudo chmod 600 /etc/myappname/myapp.env
```

4. Create systemd unit (`/etc/systemd/system/myappname.service`):
```ini
[Unit]
Description=My App Name (Flask + Streamlit)
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/myappname
EnvironmentFile=/etc/myappname/myapp.env
ExecStart=/opt/myappname/.venv/bin/python3 /opt/myappname/run.py --prod
Restart=always
RestartSec=5
KillMode=control-group
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
```

5. Enable and run:
```bash
sudo systemctl daemon-reload
sudo systemctl enable myappname.service
sudo systemctl start myappname.service
sudo systemctl status myappname.service
sudo journalctl -u myappname.service -f
```

6. Nginx site (example):
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

Then enable Nginx site and reload:
```bash
sudo ln -sf /etc/nginx/sites-available/myappname /etc/nginx/sites-enabled/myappname
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
```

### AI agent context
- [AGENTS.md](AGENTS.md)

## Common Commands
- Run app: `python3 run.py`
- Run app in production mode: `python3 run.py --prod`
- List users: `python3 scripts/manage_admin.py list`
- Create/promote admin: `python3 scripts/manage_admin.py create <username> <email> <password>`
- Kill occupied ports: `python3 scripts/kill_ports.py`

## Troubleshooting
- `Missing PostgreSQL configuration`:
  - Set `DATABASE_URL` OR all `DB_*` vars.
- Sessions reset unexpectedly:
  - Ensure `SECRET_KEY` is set and stable across restarts.
- App fails to start in production mode:
  - `SECRET_KEY` is required when running with `--prod`.
- `BuildError` in template:
  - Check `url_for('blueprint.endpoint')` names.
- Route returns 404:
  - Ensure blueprint is registered in `flask_app/__init__.py`.
- Login redirect loops:
  - Verify session cookies enabled and Flask secret key is set (already set by app factory).
- Form submit shows session-expired message:
  - Refresh page and submit again (CSRF token expired after session change).

"""
)
