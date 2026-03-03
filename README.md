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
```

Windows (cmd):
```bat
set DB_USER=appuser
set DB_PASSWORD=strongpassword
set DB_HOST=127.0.0.1
set DB_PORT=5432
set DB_NAME=appdb
```

Alternative:
```bash
export DATABASE_URL=postgresql+psycopg2://appuser:strongpassword@127.0.0.1:5432/appdb
```

### 3. Create first admin
```bash
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
│   └── db/
│       ├── __init__.py
│       ├── base.py            # db = SQLAlchemy()
│       ├── config.py          # DB URI builder
│       ├── engine.py          # shared SQL engine (raw SQL helpers)
│       ├── models.py          # ORM User model
│       └── example_crud.py    # example feature table bootstrap helper
├── templates/
├── dashboard_pages/
└── scripts/
```

## Developer Workflow

### Add a public/protected page
Use the full step-by-step guide:
- [USER_GUIDE.md](USER_GUIDE.md)

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
- `BuildError` in template:
  - Check `url_for('blueprint.endpoint')` names.
- Route returns 404:
  - Ensure blueprint is registered in `flask_app/__init__.py`.
- Login redirect loops:
  - Verify session cookies enabled and Flask secret key is set (already set by app factory).
