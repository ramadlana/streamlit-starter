# 🚀 Streamlit Starter - Secure Dashboard Wrapper

Secure wrapper for Streamlit applications using Flask and SQLite. Provides a robust authentication layer with a stunning dark glassmorphism design.
Ideal for internal business tools, it provides a simple yet secure authentication gateway to protect your Streamlit dashboards without the complexity of enterprise identity management.

---

## 🛠️ Quick Start (Development mode)

### 1. Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Initial admin setup (if needed)
python3 scripts/manage_admin.py create admin admin@example.com admin123
```

### 2. Configure Ports
Edit `.env.ports` to change default ports (default: 5001 for Flask, 8501 for Streamlit).

### 3. Run Application
The unified runner automatically cleans up zombie processes and starts both servers.

```bash
# Development Mode (Debug ON)
python3 run.py

# Production Mode (Debug OFF + Nginx Support)
python3 run.py --prod
```

---

## 🔒 Production Deployment (Ubuntu + Nginx)

Follow these steps to deploy on a clean Ubuntu server.

### 1. System Preparation
```bash
sudo apt update && sudo apt install python3-pip python3-venv nginx -y
git clone https://github.com/ramadlana/streamlit-starter.git
cd streamlit-starter
```

### 2. Environment Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 scripts/manage_admin.py create admin admin@admin.com admin123
```

### 3. Nginx Configuration
Create a config file: `sudo nano /etc/nginx/sites-available/streamlitpro`
```nginx
server {
    listen 80;
    server_name _; # Use '_' to catch all traffic or your actual domain/IP

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
 
**CRITICAL: Enable the site and remove the default Nginx page:**
```bash
# 1. Remove the default Nginx catch-all (important!)
sudo rm /etc/nginx/sites-enabled/default

# 2. Enable your new configuration
sudo ln -sf /etc/nginx/sites-available/streamlitpro /etc/nginx/sites-enabled/

# 3. Test and restart
sudo nginx -t && sudo systemctl restart nginx
```

---

## 🔐 Optional: SSL/HTTPS Configuration (Self-Signed)

For secure internal communication, follow these steps to enable HTTPS using a self-signed certificate.

### 1. Generate Self-Signed Certificate
Run this command to create a certificate that lasts for one year:
```bash
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/nginx-selfsigned.key \
  -out /etc/ssl/certs/nginx-selfsigned.crt
```
*(You will be asked for some information; you can leave them blank or fill them in).*

### 2. Update Nginx Configuration
Replace `/etc/nginx/sites-available/streamlitpro` with this HTTPS version:
```nginx
server {
    listen 80;
    server_name _;
    return 301 https://$host$request_uri; # Redirect HTTP to HTTPS
}

server {
    listen 443 ssl;
    server_name _;

    ssl_certificate /etc/ssl/certs/nginx-selfsigned.crt;
    ssl_certificate_key /etc/ssl/private/nginx-selfsigned.key;

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

### 3. Restart Nginx
```bash
sudo nginx -t && sudo systemctl restart nginx
```

### 4. Security & Cleanup
```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow 22
sudo ufw deny 5001
sudo ufw deny 8501
sudo ufw enable

# Clear any stuck ports
python3 scripts/kill_ports.py
```

### 5. Run for Production
Use `nohup` or `screen` to keep the app running after closing the terminal:
```bash
nohup python3 run.py --prod > app.log 2>&1 &
```
*(Alternatively, use a tool like `pm2` or `systemd` for professional process management).*

### 6. Open web page
Open browser `http://yourserverip/` (or `https://yourserverip/` if SSL is configured).
**Note:** Browser will warn you about the self-signed certificate. Click "Advanced" and "Proceed" to continue.

**Default Credentials:**
- **Username:** `admin`
- **Password:** `admin123`

---

## 🛡️ Admin & Tools

### 🏠 Admin Panel
Accessed at `/admin` (requires admin account). Manage users, reset passwords, and assign roles via the UI.

### 🖥️ CLI Utilities
- **User Management**: `python3 scripts/manage_admin.py list` or `create`.
- **Port Cleanup**: `python3 scripts/kill_ports.py` (Kills any processes stuck on configured ports).

## 📂 Project Structure
- `run.py`: Hybrid entry point (Dev/Prod). Supports automatic port cleanup.
- `auth_server.py`: Flask Authentication & Gateway logic.
- `dashboard_app.py`: Streamlit application entry point.
- `dashboard_pages/`: All Streamlit UI content and multi-page files.
- `models.py`: Database schema and encryption.
- `scripts/`: Management scripts (`kill_ports.py`, `manage_admin.py`).
- `.env.ports`: Centralized port configuration.
- `templates/`: Premium glassmorphism HTML templates.
