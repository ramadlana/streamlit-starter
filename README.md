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

## 📂 Project Structure
- `app_flask.py`: Flask authentication logic, user management routes, and dashboard routing.
- `app.py`: Core Streamlit application logic.
- `models.py`: Database schema (User model with roles).
- `manage_admin.py`: Terminal-based administrative tool.
- `run.py`: Unified development runner script.
- `templates/`: Premium glassmorphism HTML templates (Admin, Login, Signup, Dashboard).
- `instance/users.db`: Secure SQLite database for user storage.
