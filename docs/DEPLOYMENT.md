# Production Deployment Guide

This guide covers deploying the app on a **Linux server** behind Nginx, with systemd. For **development** on your PC (Windows, Linux, or macOS), see **[../README.md](../README.md)** — Quick Start (Development).

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Server (Production) Deployment](#2-server-production-deployment)
3. [Environment Variables Reference](#3-environment-variables-reference)
4. [Troubleshooting](#4-troubleshooting)

---

## 1. Prerequisites

- **Linux** (e.g. Ubuntu 22.04, Debian 12)
- **Nginx** installed
- **PostgreSQL** (local or remote; ensure firewall/security)
- **Python 3.10+** and `venv`

---

## 2. Server (Production) Deployment

The app runs with `python3 run.py --prod` and expects Nginx to proxy Flask and Streamlit (under `/streamlit/`).

### 2.1 Install app and dependencies

```bash
# Example: deploy under /opt
sudo mkdir -p /opt/streamgatekeeper
sudo chown "$USER" /opt/streamgatekeeper
cd /opt/streamgatekeeper

git clone https://github.com/ramadlana/streamlit-starter .
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Adjust path and repo URL to your setup.

### 2.2 Environment file (production)

Create a dedicated env file so systemd can load it (e.g. `/etc/streamgatekeeper/streamgatekeeper.env`):

```bash
sudo mkdir -p /etc/streamgatekeeper
sudo nano /etc/streamgatekeeper/streamgatekeeper.env
```

Contents (replace with real values):

```bash
DATABASE_URL=postgresql+psycopg2://appuser:strongpassword@127.0.0.1:5432/appdb
SECRET_KEY=replace-with-a-long-random-secret
FLASK_PORT=5001
STREAMLIT_PORT=8501
```

Secure the file:

```bash
sudo chown root:root /etc/streamgatekeeper/streamgatekeeper.env
sudo chmod 600 /etc/streamgatekeeper/streamgatekeeper.env
```

**Important:** Use a strong, unique `SECRET_KEY`. The app will not start in production mode without it.

### 2.3 Create admin user (once)

With the venv activated and env vars loaded:

```bash
cd /opt/streamgatekeeper
source .venv/bin/activate
export $(grep -v '^#' /etc/streamgatekeeper/streamgatekeeper.env | xargs)
python3 scripts/manage_admin.py create admin admin@example.com <secure-password>
```

### 2.4 systemd unit

Create a service so the app runs on boot and restarts on failure.

**File:** `/etc/systemd/system/streamgatekeeper.service`

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

Adjust `User`/`Group`, `WorkingDirectory`, and `ExecStart` if your paths differ. Ensure `User` has read access to the app directory and (if used) read access to the env file.

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable streamgatekeeper
sudo systemctl start streamgatekeeper
sudo systemctl status streamgatekeeper
```

### 2.5 Nginx configuration (HTTPS)

Nginx serves the app over **HTTPS** and proxies to Flask and Streamlit. HTTP is redirected to HTTPS.

**Obtain TLS certificates** (e.g. Let’s Encrypt with certbot):

```bash
# Example: certbot for Nginx (install certbot and python3-certbot-nginx first)
sudo certbot certonly --nginx -d your-domain.example.com
```

Certificates are typically under `/etc/letsencrypt/live/your-domain.example.com/`.

**File:** e.g. `/etc/nginx/sites-available/streamgatekeeper` (symlink into `sites-enabled`)

Replace `your-domain.example.com` and the certificate paths with your domain and paths.

```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.example.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS
server {
    listen 443 ssl;
    server_name your-domain.example.com;

    ssl_certificate     /etc/letsencrypt/live/your-domain.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.example.com/privkey.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;

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

    location /streamlit/ {
        auth_request /auth-check;
        proxy_pass http://127.0.0.1:8501/streamlit/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

Reload Nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### 2.6 Production checklist

| Step | Action |
|------|--------|
| 1 | Install Nginx, PostgreSQL, Python 3.10+ on server |
| 2 | Deploy app (e.g. `/opt/streamgatekeeper`), create venv, `pip install -r requirements.txt` |
| 3 | Create env file with `DATABASE_URL`, `SECRET_KEY`, `FLASK_PORT`, `STREAMLIT_PORT`; secure permissions |
| 4 | Create first admin with `manage_admin.py create` |
| 5 | Install and enable systemd unit; start service |
| 6 | Obtain TLS certs (e.g. certbot), configure Nginx for HTTPS (proxy `/` to Flask, `/streamlit/` to Streamlit, HTTP→HTTPS redirect); reload Nginx |
| 7 | Open https://your-domain and log in |

---

## 3. Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes* | — | Full PostgreSQL URL, e.g. `postgresql+psycopg2://user:pass@host:5432/dbname` |
| `DB_USER` | Yes* | — | PostgreSQL user (if not using `DATABASE_URL`) |
| `DB_PASSWORD` | Yes* | — | PostgreSQL password |
| `DB_HOST` | Yes* | — | PostgreSQL host |
| `DB_PORT` | Yes* | — | PostgreSQL port |
| `DB_NAME` | Yes* | — | Database name |
| `SECRET_KEY` | Yes (prod) | — | Flask secret; **must** set in production |
| `FLASK_PORT` | No | `5001` | Port for Flask |
| `STREAMLIT_PORT` | No | `8501` | Port for Streamlit |
| `FLASK_DEBUG` | No | Set by run mode | `False` for `run.py --prod` |

\* Provide either `DATABASE_URL` or all of `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`.

---

## 4. Troubleshooting

### Missing PostgreSQL configuration

Set either `DATABASE_URL` or all of `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`. Ensure the database and user exist and the server is reachable.

### SECRET_KEY / production boot error

In production (`run.py --prod`), `FLASK_DEBUG` is off and `SECRET_KEY` is required. Set a long random value in your env file.

### Session resets or “session expired” on forms

Use a stable `SECRET_KEY` across restarts. For forms, ensure every POST form includes the CSRF token:  
`<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">`.

### Streamlit not loading in production

- Ensure Nginx is proxying `/streamlit/` to `http://127.0.0.1:8501/streamlit/` with WebSocket headers (`Upgrade`, `Connection`).
- Ensure the app is started with `run.py --prod` so Streamlit uses `--server.baseUrlPath /streamlit/`.
- Check that the systemd service is running: `sudo systemctl status streamgatekeeper`.

### 502 Bad Gateway

Flask or Streamlit is not listening. Check:

- `systemctl status streamgatekeeper`
- Ports 5001 and 8501: `ss -tlnp | grep -E '5001|8501'` (Linux)
- Logs: `journalctl -u streamgatekeeper -f`

### After code or env changes

```bash
cd /opt/streamgatekeeper
source .venv/bin/activate
pip install -r requirements.txt   # if deps changed
sudo systemctl restart streamgatekeeper
```

---

## See also

- [../README.md](../README.md) — development quick start, routes, project layout
- [AGENTS.md](AGENTS.md) — repo map and playbooks for contributors
- [FRAMEWORK_GUIDE.md](FRAMEWORK_GUIDE.md) — auth, roles, adding pages
