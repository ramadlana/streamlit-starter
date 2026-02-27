# StreamlitPro - Secure Dashboard wrapper

A premium, secure wrapper for Streamlit applications using Flask, Flask-Login, and SQLite. This project provides a robust authentication layer with a stunning dark glassmorphism design.

## 🌟 Features
- **Secure Authentication**: Flask-Login based session management.
- **SQLite Database**: Local user storage with password hashing (Werkzeug).
- **Premium UI**: Dark-themed dashboard with Inter typography and smooth animations.
- **Embedded Streamlit**: Your Streamlit app runs securely inside a protected iframe.

---

## 🛠 Prerequisites
Ensure you have Python 3.9+ installed and a virtual environment activated.

```bash
# Clone the repository
git clone <your-repo-url>
cd streamlit-starter

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🚀 Development Run
To run the application locally for development purposes, use the unified runner script. This will start both the Flask authentication server and the Streamlit engine.

```bash
python run.py
```
- **Flask Gateway**: [http://localhost:5001](http://localhost:5001)
- **Streamlit Backend**: [http://localhost:8501](http://localhost:8501)

---

## 🛡️ Admin Management
The system includes a secure Admin Panel to manage users. Administrators can view, add, edit, and delete user accounts.

### 🏠 Admin Dashboard
Accessed at `/admin` (only visible to users with `is_admin` set to `true`).
- **User List**: Grid view of all registered users.
- **Add User**: Create new users and assign roles.
- **Edit User**: Modify existing account details or reset passwords.
- **Delete User**: Remove accounts (protected against self-deletion).

### 🖥️ Terminal Admin Script
For high-security operations, you can manage administrators directly from the server terminal.

```bash
# List all users and their status
python manage_admin.py list

# Create a new admin or promote/reset an existing one
python manage_admin.py create <username> <email> <password>
```

---

## 🔒 Production Deployment (Nginx)

For production, it is critical to hide the Streamlit port (8501) and the Flask port (5001) from the public internet and use Nginx as a reverse proxy.

### 1. Nginx Configuration
Create a new Nginx configuration file (e.g., `/etc/nginx/sites-available/streamlitpro`):

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # 1. Flask Authentication Gateway
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 2. Lightweight Auth Check for Nginx
    # This endpoint returns 200 OK if logged in, 401 Unauthorized if not.
    location = /auth-check {
        internal;
        proxy_pass http://127.0.0.1:5001/auth-check;
        proxy_pass_request_body off;
        proxy_set_header Content-Length "";
        proxy_set_header X-Original-URI $request_uri;
    }

    # 3. Protected Streamlit App
    location /dashboard-app/ {
        auth_request /auth-check;
        error_page 401 = @error401;

        proxy_pass http://127.0.0.1:8501/dashboard-app/;
        
        # REQUIRED for Streamlit WebSockets
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # Redirect to login if unauthorized
    location @error401 {
        return 302 /login;
    }
}
```

### 2. Startup Command (Production Mode)
Use the unified runner with the `--prod` flag. This disables Flask debug mode and configures Streamlit correctly for the Nginx proxy path.

```bash
python run.py --prod
```

### 3. Firewall Security (UFW)
Ensure only Nginx is accessible from the outside.

```bash
# Allow Nginx
sudo ufw allow 'Nginx Full'

# Deny direct access to backend ports
sudo ufw deny 8501
sudo ufw deny 5001

# Enable firewall
sudo ufw enable
```

---

## 📂 Project Structure
- `run.py`: Hybrid runner. Supports `python run.py` (Dev) and `python run.py --prod` (Production).
- `auth_server.py`: Flask auth logic + `/auth-check` endpoint for Nginx security.
- `dashboard_app.py`: Main Streamlit entry point.
- `dashboard_pages/`: Folder containing all Streamlit UI content and pages.
- `models.py`: Database schema and password hashing logic.
- `scripts/`: Administrative and management scripts.
- `templates/`: Premium glassmorphism HTML templates (Flask wrapper).
- `instance/users.db`: SQLite database for user storage.

