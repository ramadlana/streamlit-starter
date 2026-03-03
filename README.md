# Streamlit Starter

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

## Quick Start

### 1. Install
```bash
pip install -r requirements.txt
```

### 2. Set database env vars
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

Alternative:
```bash
export DATABASE_URL=postgresql+psycopg2://appuser:strongpassword@127.0.0.1:5432/appdb
```

### 3. Activate venv and create first admin
```bash
source .venv/bin/activate  # adjust if your venv path/name differs
python3 scripts/manage_admin.py create admin admin@example.com admin123
```

### 4. Run app
```bash
python3 run.py
```

- Flask: `http://127.0.0.1:5001`
- Streamlit proxied behind Flask after login

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

### Add a public/protected page
Use this pattern:
1. Create `flask_app/routes/<feature>.py` with a blueprint.
2. Add public/protected routes (`@login_required` for protected).
3. Register blueprint in `flask_app/__init__.py`.
4. Add matching templates in `templates/`.
5. Use explicit `url_for("blueprint.endpoint")` names.

### Deployment (Nginx + systemd on `/opt`)

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
