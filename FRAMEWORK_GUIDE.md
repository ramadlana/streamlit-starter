# User Guide — Internal Web Framework

This guide explains how to use this framework to build authenticated, role-protected Flask pages and Streamlit dashboards for your internal tools.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Authentication (Login / Signup / Logout)](#2-authentication)
3. [Protecting Pages with `@login_required`](#3-protecting-pages-with-login_required)
4. [Roles & Authorization](#4-roles--authorization)
5. [Using the `@role_required` Decorator](#5-using-the-role_required-decorator)
6. [Adding a New Role](#6-adding-a-new-role)
7. [Adding a New Protected Flask Page](#7-adding-a-new-protected-flask-page)
8. [Adding a Role-Restricted Page](#8-adding-a-role-restricted-page)
9. [CSRF Protection on Forms](#9-csrf-protection-on-forms)
10. [Embedding Streamlit via iframe (Protected Dashboard)](#10-embedding-streamlit-via-iframe)
11. [Adding a New Streamlit Dashboard Page](#11-adding-a-new-streamlit-dashboard-page)
12. [Navigation Bar — Showing/Hiding Links by Role](#12-navigation-bar--showinghiding-links-by-role)
13. [Managing Users (Admin Panel & CLI)](#13-managing-users)
14. [Adding a Full CRUD Feature](#14-adding-a-full-crud-feature)
15. [Database Access Patterns](#15-database-access-patterns)
16. [Environment Variables](#16-environment-variables)

---

## 1. Architecture Overview

The app runs **two processes** started by `run.py`:

| Process | File | Default Port | Purpose |
|---------|------|-------------|---------|
| **Flask** | `auth_server.py` | `5001` | Authentication gateway, HTML pages, API |
| **Streamlit** | `dashboard_app.py` | `8501` | Data dashboards (embedded inside Flask via iframe) |

In **development**, users visit `http://localhost:5001`. The home page loads the Streamlit dashboard inside an iframe pointing to `localhost:8501`.

In **production** (`python3 run.py --prod`), Streamlit is reverse-proxied behind `/dashboard-app/` (typically via Nginx), so the iframe URL becomes `/dashboard-app/` instead.

### Key directories

```
flask_app/              ← Flask app factory + extensions
flask_app/routes/       ← Blueprints (one file per feature)
app_db/                 ← Database models, helpers, engine
templates/              ← Jinja2 HTML templates
static/css/             ← Stylesheets
dashboard_pages/        ← Streamlit page modules
scripts/                ← CLI utilities (manage_admin, etc.)
```

---

## 2. Authentication

Authentication is handled by **Flask-Login**. The implementation lives in `flask_app/routes/auth.py`.

### How it works

- **User model** (`app_db/models.py`): stores `username`, `email`, `password` (hashed), and `role`.
- **Password hashing**: uses `werkzeug.security.generate_password_hash` / `check_password_hash`.
- **Session management**: Flask-Login tracks the logged-in user via a secure session cookie.

### Built-in auth routes

| Route | Method | What it does |
|-------|--------|--------------|
| `/login` | GET/POST | Login form + credential check |
| `/signup` | GET/POST | Self-service registration (default role: `viewer`) |
| `/logout` | GET | Logs out the current user |
| `/auth-check` | GET | Returns `200 Authenticated` or `401 Unauthorized` |

### User loader (required by Flask-Login)

> **FRAMEWORK CODE** — `flask_app/routes/auth.py` — already configured, no changes needed.

```python
# flask_app/routes/auth.py
@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))
```

This callback tells Flask-Login how to reload a user from the session. It is already configured — you do not need to change it.

### Login flow

> **FRAMEWORK CODE** — `flask_app/routes/auth.py` — already configured, no changes needed.

```python
# flask_app/routes/auth.py
@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home.index"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)                         # ← sets session
            return redirect(url_for("home.index"))
        flash("Invalid username or password")

    return render_template("login.html")
```

---

## 3. Protecting Pages with `@login_required`

Any route that should only be accessible to logged-in users must use the `@login_required` decorator from Flask-Login.

### Example — existing home page

> **FRAMEWORK CODE** — `flask_app/routes/home.py` — already configured, no changes needed.

```python
# flask_app/routes/home.py
from flask_login import login_required

@bp.route("/")
@login_required
def index():
    ...
```

If an unauthenticated user visits `/`, Flask-Login automatically redirects them to the login page (configured via `login_manager.login_view = "auth.login"` in the app factory).

### How to protect your own page

> **YOUR CODE** — write this in your own blueprint file, e.g. `flask_app/routes/my_feature.py`.

```python
from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint("my_feature", __name__)

@bp.route("/my-feature")
@login_required
def my_feature_page():
    return render_template("my_feature.html")
```

> **Rule**: Always place `@login_required` directly **after** the `@bp.route(...)` decorator.

---

## 4. Roles & Authorization

### Available roles

Defined in `app_db/user_roles.py`:

> **FRAMEWORK CODE** — `app_db/user_roles.py` — modify only when adding a new role (see [Section 6](#6-adding-a-new-role)).

```python
ROLE_CHOICES = ("viewer", "editor", "approval1", "approval2", "admin")
```

| Role | Typical permissions |
|------|-------------------|
| `viewer` | Read-only access; default for new sign-ups |
| `editor` | Can create/edit docs and access editor menus |
| `approval1` | Same as editor (used for approval workflows) |
| `approval2` | Same as editor (used for approval workflows) |
| `admin` | Full access; user management, housekeeping |

### How roles are stored

Each `User` record has a `role` column (VARCHAR). The `normalize_role()` function ensures any unknown value falls back to `"viewer"`:

> **FRAMEWORK CODE** — `app_db/user_roles.py` — no changes needed.

```python
# app_db/user_roles.py
def normalize_role(value: str) -> str:
    candidate = (value or "").strip().lower()
    if candidate in ALLOWED_ROLES:
        return candidate
    return DEFAULT_ROLE  # "viewer"
```

### Setting a user's role

```python
user.set_role("editor")   # normalizes + stores
db.session.commit()
```

---

## 5. Using the `@role_required` Decorator

The framework provides a `role_required` decorator in `flask_app/routes/permissions.py`.

### Signature

> **FRAMEWORK CODE** — `flask_app/routes/permissions.py` — no changes needed. Just import and use it.

```python
role_required(*allowed_roles, message="Access denied.")
```

- Pass **one or more role strings** as positional arguments.
- Users whose role matches **any** of the allowed roles are granted access.
- Everyone else sees a flash message and is redirected to the home page.

### Example — Admin-only route

> **FRAMEWORK CODE** — `flask_app/routes/admin.py` — already configured, no changes needed. Shown as reference.

```python
# flask_app/routes/admin.py
from flask_app.routes.permissions import role_required

@bp.route("/admin")
@login_required
@role_required("admin", message="Access denied: Admins only.")
def admin():
    users = User.query.all()
    return render_template("admin.html", users=users, roles=ROLE_CHOICES)
```

### Example — Multiple roles allowed

> **FRAMEWORK CODE** — `flask_app/routes/docs.py` — already configured, no changes needed. Shown as reference.

```python
# flask_app/routes/docs.py
@bp.route("/docs/editor/<int:doc_id>", methods=["GET", "POST"])
@login_required
@role_required(
    "editor",
    "approval1",
    "approval2",
    "admin",
    message="Access denied: You only have view permission for docs.",
)
def docs_editor(doc_id: int):
    ...
```

### Shortcut — `admin_required`

> **YOUR CODE** — use this shortcut when you only need admin access.

```python
from flask_app.routes.permissions import admin_required

@bp.route("/my-admin-page")
@login_required
@admin_required()
def my_admin_page():
    ...
```

### Decorator stacking order

Always follow this order:

```python
@bp.route("/path")         # 1. Route
@login_required             # 2. Must be logged in
@role_required("admin")     # 3. Must have the right role
def my_view():
    ...
```

---

## 6. Adding a New Role

### Step 1 — Update `ROLE_CHOICES`

> **YOUR CODE** — edit the existing file `app_db/user_roles.py` to add your new role.

```python
# Before
ROLE_CHOICES = ("viewer", "editor", "approval1", "approval2", "admin")

# After — example: adding "manager"
ROLE_CHOICES = ("viewer", "editor", "approval1", "approval2", "manager", "admin")
```

`ALLOWED_ROLES` is derived from `ROLE_CHOICES` automatically (framework handles this):

```python
ALLOWED_ROLES = set(ROLE_CHOICES)
```

### Step 2 — Use the new role in routes

> **YOUR CODE** — write this in your own blueprint file.

```python
@bp.route("/manager-dashboard")
@login_required
@role_required("manager", "admin")
def manager_dashboard():
    return render_template("manager_dashboard.html")
```

### Step 3 — Update nav visibility in `templates/base.html`

> **YOUR CODE** — add this inside the authenticated block in `templates/base.html`.

```html
{% if current_user.role in ['manager', 'admin'] %}
<a href="{{ url_for('my_feature.manager_dashboard') }}">Manager Dashboard</a>
{% endif %}
```

### Step 4 — Assign the role to users

Via the Admin Panel UI or the CLI:

```bash
# Promote existing user via admin panel (browser), or:
python3 scripts/manage_admin.py create <username> <email> <password>
# Then edit their role in the Admin Panel
```

---

## 7. Adding a New Protected Flask Page

Full step-by-step for a new feature page visible to all logged-in users.

### Step 1 — Create the blueprint

> **YOUR CODE** — create a new file `flask_app/routes/my_feature.py`.

```python
from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint("my_feature", __name__)


@bp.route("/my-feature")
@login_required
def my_feature_page():
    return render_template("my_feature/index.html")
```

### Step 2 — Create the template

> **YOUR CODE** — create a new file `templates/my_feature/index.html`.

```html
{% extends "base.html" %}

{% block title %}My Feature{% endblock %}

{% block content %}
<h1>My Feature</h1>
<p>This page is only visible to logged-in users.</p>
{% endblock %}
```

### Step 3 — Register the blueprint

> **YOUR CODE** — add these lines to the existing `flask_app/__init__.py`.

```python
from flask_app.routes.my_feature import bp as my_feature_bp

# Inside create_app(), add:
app.register_blueprint(my_feature_bp)
```

### Step 4 — Add a nav link

> **YOUR CODE** — add this to `templates/base.html`, inside the `{% if current_user.is_authenticated %}` block.

```html
<a href="{{ url_for('my_feature.my_feature_page') }}">My Feature</a>
```

---

## 8. Adding a Role-Restricted Page

Same as above, but add `@role_required` and conditionally show the nav link.

### Route

> **YOUR CODE** — write this in your own blueprint file.

```python
from flask_app.routes.permissions import role_required

@bp.route("/reports")
@login_required
@role_required("editor", "admin", message="You do not have access to reports.")
def reports():
    return render_template("reports/index.html")
```

### Nav link (only visible to allowed roles)

> **YOUR CODE** — add this to `templates/base.html`.

```html
<!-- templates/base.html -->
{% if current_user.role in ['editor', 'admin'] %}
<a href="{{ url_for('my_feature.reports') }}">Reports</a>
{% endif %}
```

---

## 9. CSRF Protection on Forms

Every `POST` form **must** include a CSRF token. The framework uses Flask-WTF's `CSRFProtect`.

### Required hidden field in every form

> **YOUR CODE** — you must include this hidden input in every POST form you create.

```html
<form method="POST" action="/my-endpoint">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    <!-- other fields -->
    <button type="submit">Submit</button>
</form>
```

If you forget this, the form submission will fail with a "session expired" flash message.

### How it's set up

> **FRAMEWORK CODE** — `flask_app/__init__.py` — already configured, no changes needed.

```python
# flask_app/__init__.py
csrf.init_app(app)

@app.context_processor
def inject_csrf_token():
    return {"csrf_token": generate_csrf}
```

---

## 10. Embedding Streamlit via iframe

The home page (`/`) demonstrates the iframe-protection pattern: Flask authenticates the user, then renders a full-screen Streamlit iframe.

### How it works

> **FRAMEWORK CODE** — `flask_app/routes/home.py` — already configured, no changes needed.

```python
# flask_app/routes/home.py
@bp.route("/")
@login_required
def index():
    streamlit_port = os.environ.get("STREAMLIT_PORT", "8501")
    streamlit_url = f"http://localhost:{streamlit_port}"
    if not current_app.debug:
        streamlit_url = "/dashboard-app/"
    return render_template("index.html", streamlit_url=streamlit_url)
```

> **FRAMEWORK CODE** — `templates/index.html` — already configured, no changes needed.

```html
<!-- templates/index.html -->
{% extends "base.html" %}
{% block content %}
<iframe src="{{ streamlit_url }}" class="app-viewport"
    onload="...">
</iframe>
{% endblock %}
```

### Key points

- The `@login_required` on the Flask route ensures only authenticated users see the iframe.
- Streamlit itself has **no authentication** — it is protected because it is only reachable through the authenticated Flask shell.
- In production, Nginx proxies `/dashboard-app/` to the Streamlit port, and Streamlit is not exposed directly.

### Embedding another internal tool the same way

> **YOUR CODE** — write this in your own blueprint to wrap any internal tool behind auth.

```python
@bp.route("/internal-tool")
@login_required
@role_required("admin")
def internal_tool():
    tool_url = "http://localhost:9000"  # your internal tool
    return render_template("iframe_wrapper.html", iframe_url=tool_url)
```

> **YOUR CODE** — create `templates/iframe_wrapper.html`.

```html
<!-- templates/iframe_wrapper.html -->
{% extends "base.html" %}
{% block content %}
<iframe src="{{ iframe_url }}" style="width:100%; height:calc(100vh - 60px); border:none;"></iframe>
{% endblock %}
```

---

## 11. Adding a New Streamlit Dashboard Page

### Step 1 — Create the page module

> **YOUR CODE** — create a new file `dashboard_pages/my_dashboard.py`.

```python
import streamlit as st

st.title("My Dashboard")
st.write("Hello from the new dashboard page.")
```

### Step 2 — Register in `dashboard_app.py`

> **YOUR CODE** — add these lines to the existing `dashboard_app.py`.

```python
# Add page definition
my_dashboard_page = st.Page(
    "dashboard_pages/my_dashboard.py",
    title="My Dashboard",
    icon=":material/bar_chart:",
)

# Add to navigation group
pg = st.navigation(
    {
        "Main Menu": [home_page, my_dashboard_page],
        "Example": [basic_page, ...],
    }
)
```

The Streamlit dashboard is already protected by the Flask `@login_required` on the home route — no extra auth needed.

---

## 12. Navigation Bar — Showing/Hiding Links by Role

The nav bar in `templates/base.html` uses Jinja conditionals to show links based on the user's role.

### Existing patterns

**Show to all authenticated users:**

> **FRAMEWORK CODE** — `templates/base.html` — already configured. Shown as reference.

```html
{% if current_user.is_authenticated %}
<a href="{{ url_for('docs.docs_index') }}">Docs</a>
{% endif %}
```

**Show only to editors and above (dropdown menu):**

> **FRAMEWORK CODE** — `templates/base.html` — already configured. Shown as reference.

```html
{% if current_user.role in ['editor', 'approval1', 'approval2', 'admin'] %}
<div class="nav-dropdown">
    <button class="nav-dropdown-toggle" type="button">
        Editor Menu <span class="nav-dropdown-caret">▾</span>
    </button>
    <div class="nav-dropdown-menu">
        <a href="{{ url_for('example_crud.example_crud') }}">Example CRUD</a>
        <a href="{{ url_for('dummydata_crud.dummydata_crud') }}">Dummydata CRUD</a>
    </div>
</div>
{% endif %}
```

**Show only to admins:**

> **FRAMEWORK CODE** — `templates/base.html` — already configured. Shown as reference.

```html
{% if current_user.role == "admin" %}
<a href="{{ url_for('admin.admin') }}">Admin Panel</a>
{% endif %}
```

### Adding your own nav link

> **YOUR CODE** — add this to `templates/base.html` for your custom feature.

```html
{% if current_user.role in ['manager', 'admin'] %}
<a href="{{ url_for('my_feature.reports') }}">Reports</a>
{% endif %}
```

---

## 13. Managing Users

### Via the Admin Panel (browser)

1. Log in as an `admin` user.
2. Click **Admin Panel** in the nav bar.
3. From there you can **Add**, **Edit** (change role/password), or **Delete** users.

### Via the CLI

```bash
# Create or promote a user to admin
python3 scripts/manage_admin.py create <username> <email> <password>

# List all users
python3 scripts/manage_admin.py list
```

---

## 14. Adding a Full CRUD Feature

The framework includes two CRUD examples you can copy as a starting pattern.

### Using ORM (`example_crud` pattern — raw SQL)

See `flask_app/routes/example_crud.py`. This uses raw SQL via `get_sql_engine()` and is suitable for feature-scoped tables.

### Step-by-step

1. **Create blueprint** — `flask_app/routes/<feature>.py`
2. **Create DB helper** — `app_db/<feature>.py` (table bootstrap + queries)
3. **Create template** — `templates/<feature>.html`
4. **Register blueprint** — in `flask_app/__init__.py`
5. **Add nav link** — in `templates/base.html`

### Full CRUD route example

> **YOUR CODE** — create a new file `flask_app/routes/my_crud.py` using this as a starting template.

```python
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app_db import get_sql_engine

bp = Blueprint("my_crud", __name__)


# ---------------------------------------------------------------------------
# LIST — show all items
# ---------------------------------------------------------------------------
@bp.route("/my-crud")
@login_required
def list_items():
    try:
        with get_sql_engine().connect() as conn:
            items = conn.execute(
                text("SELECT id, name, description, created_at FROM my_table ORDER BY id DESC")
            ).mappings().all()
    except (RuntimeError, SQLAlchemyError) as exc:
        flash(f"Database error: {exc}")
        items = []
    return render_template("my_crud.html", items=items)


# ---------------------------------------------------------------------------
# CREATE — insert a new item
# ---------------------------------------------------------------------------
@bp.route("/my-crud/create", methods=["POST"])
@login_required
def create_item():
    name = (request.form.get("name") or "").strip()
    description = (request.form.get("description") or "").strip()

    if not name:
        flash("Name is required.")
        return redirect(url_for("my_crud.list_items"))

    try:
        with get_sql_engine().begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO my_table (name, description)
                    VALUES (:name, :description)
                    """
                ),
                {"name": name, "description": description or None},
            )
        flash("Item created.")
    except (RuntimeError, SQLAlchemyError) as exc:
        flash(f"Create failed: {exc}")
    return redirect(url_for("my_crud.list_items"))


# ---------------------------------------------------------------------------
# EDIT / UPDATE — modify an existing item
# ---------------------------------------------------------------------------
@bp.route("/my-crud/edit/<int:item_id>", methods=["POST"])
@login_required
def edit_item(item_id):
    name = (request.form.get("name") or "").strip()
    description = (request.form.get("description") or "").strip()

    if not name:
        flash("Name is required.")
        return redirect(url_for("my_crud.list_items"))

    try:
        with get_sql_engine().begin() as conn:
            updated = conn.execute(
                text(
                    """
                    UPDATE my_table
                    SET name = :name,
                        description = :description
                    WHERE id = :item_id
                    """
                ),
                {
                    "name": name,
                    "description": description or None,
                    "item_id": item_id,
                },
            )
        flash("Item updated." if updated.rowcount else "Item not found.")
    except (RuntimeError, SQLAlchemyError) as exc:
        flash(f"Update failed: {exc}")
    return redirect(url_for("my_crud.list_items"))


# ---------------------------------------------------------------------------
# DELETE — remove an item
# ---------------------------------------------------------------------------
@bp.route("/my-crud/delete/<int:item_id>", methods=["POST"])
@login_required
def delete_item(item_id):
    try:
        with get_sql_engine().begin() as conn:
            deleted = conn.execute(
                text("DELETE FROM my_table WHERE id = :item_id"),
                {"item_id": item_id},
            )
        flash("Item deleted." if deleted.rowcount else "Item not found.")
    except (RuntimeError, SQLAlchemyError) as exc:
        flash(f"Delete failed: {exc}")
    return redirect(url_for("my_crud.list_items"))
```

### Template example with Edit/Delete actions

> **YOUR CODE** — create `templates/my_crud.html` to display the table with action buttons.

```html
{% extends "base.html" %}

{% block title %}My CRUD{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/form_and_table.css') }}">
{% endblock %}

{% block content %}

<div class="crud-container">
    <div class="crud-header">
        <div>
            <h1>My CRUD</h1>
            <p class="subtitle">Manage items in the my_table table.</p>
        </div>
    </div>

    {% with messages = get_flashed_messages() %}
    {% if messages %}
    {% for message in messages %}
    <div class="flash-message">{{ message }}</div>
    {% endfor %}
    {% endif %}
    {% endwith %}

    <div class="crud-grid">
        <!-- Column 1: Items table -->
        <div class="crud-panel">
            <h3 style="font-size: 0.95rem; margin-bottom: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-secondary);">
                Items
            </h3>
            <div class="crud-table-wrapper">
                <table class="crud-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Column 1 (Name)</th>
                            <th>Column 2 (Description)</th>
                            <th>Actions</th>
                            <th>Created</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for item in items %}
                        <tr>
                            <td>{{ item.id }}</td>
                            <td title="{{ item.name }}">{{ item.name }}</td>
                            <td title="{{ item.description or '' }}">
                                {% if item.description %}
                                    {{ item.description[:80] }}{% if item.description|length > 80 %}…{% endif %}
                                {% else %}
                                    <span style="color: var(--text-secondary); opacity: 0.7;">No description</span>
                                {% endif %}
                            </td>
                        
                            <!-- ACTION COLUMN with Edit and Delete buttons -->
                            <td>
                                <div class="actions">
                                    <!-- Edit button (opens form on the right) -->
                                    <button
                                        type="button"
                                        class="btn btn-small btn-ghost row-edit-btn"
                                        data-id="{{ item.id }}"
                                        data-name="{{ item.name }}"
                                        data-description="{{ item.description or '' }}"
                                    >
                                        Edit
                                    </button>
                                    
                                    <!-- Delete button (submits DELETE form) -->
                                    <form method="POST" action="{{ url_for('my_crud.delete_item', item_id=item.id) }}"
                                        onsubmit="return confirm('Delete this item?');">
                                        <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                                        <button class="btn btn-small btn-danger" type="submit">Delete</button>
                                    </form>
                                </div>
                            </td>
                            <td>{{ item.created_at }}</td>
                        </tr>
                        {% else %}
                        <tr>
                            <td colspan="5" style="color: var(--text-secondary);">No rows yet.</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Column 2: Create/Edit form -->
        <div class="crud-panel">
            <h3 id="item-form-title" style="font-size: 0.95rem; margin-bottom: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-secondary);">
                New Item
            </h3>
            <form
                id="item-form"
                class="form-compact"
                method="POST"
                action="{{ url_for('my_crud.create_item') }}"
                data-create-url="{{ url_for('my_crud.create_item') }}"
                data-edit-url-prefix="/my-crud/edit/"
            >
                <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                <input type="hidden" id="item-id" value="">
                
                <!-- Column 1 input -->
                <div class="form-group">
                    <label>Column 1 (Name)</label>
                    <input type="text" name="name" id="item-name" required />
                </div>
                
                <!-- Column 2 input -->
                <div class="form-group" style="margin-bottom: 0.75rem;">
                    <label>Column 2 (Description)</label>
                    <textarea name="description" id="item-description" placeholder="Optional description"></textarea>
                </div>
                
                <button class="btn" type="submit" id="item-submit">Create item</button>
                <button
                    type="button"
                    class="btn btn-ghost"
                    id="item-cancel-edit"
                    style="width: 100%; margin-top: 0.5rem; display: none;"
                >
                    Cancel edit
                </button>
            </form>
        </div>
    </div>
</div>

<script>
    (function () {
        const form = document.getElementById('item-form');
        if (!form) return;

        const titleEl = document.getElementById('item-form-title');
        const idInput = document.getElementById('item-id');
        const nameInput = document.getElementById('item-name');
        const descInput = document.getElementById('item-description');
        const submitBtn = document.getElementById('item-submit');
        const cancelBtn = document.getElementById('item-cancel-edit');

        const createUrl = form.getAttribute('data-create-url');
        const editUrlPrefix = form.getAttribute('data-edit-url-prefix');

        // Switch to CREATE mode
        function setCreateMode() {
            idInput.value = '';
            form.action = createUrl;
            submitBtn.textContent = 'Create item';
            titleEl.textContent = 'New Item';
            cancelBtn.style.display = 'none';
            nameInput.value = '';
            descInput.value = '';
        }

        // Switch to EDIT mode (populates form with existing data)
        function setEditMode(itemId, name, description) {
            idInput.value = itemId;
            nameInput.value = name || '';
            descInput.value = description || '';
            form.action = (editUrlPrefix || '/my-crud/edit/') + itemId;
            submitBtn.textContent = 'Update item';
            titleEl.textContent = 'Edit Item';
            cancelBtn.style.display = 'block';
            nameInput.focus();
            nameInput.select();
        }

        // Handle Edit button clicks in the action column
        document.addEventListener('click', function (evt) {
            const btn = evt.target.closest('.row-edit-btn');
            if (!btn) return;
            const itemId = btn.getAttribute('data-id');
            const name = btn.getAttribute('data-name') || '';
            const description = btn.getAttribute('data-description') || '';
            if (!itemId) return;
            setEditMode(itemId, name, description);
        });

        // Cancel edit button
        cancelBtn.addEventListener('click', function () {
            setCreateMode();
        });

        // Ensure initial state is create mode
        setCreateMode();
    })();
</script>
{% endblock %}
```

**How it works:**

1. **Action column** contains Edit and Delete buttons
2. **Edit button** (`row-edit-btn`) opens the form on the right with the item's data
3. **Delete button** submits a POST to the `delete_item` route with CSRF token
4. **Form** switches between CREATE and UPDATE modes based on hidden `item-id` field
5. **JavaScript** handles the Edit button clicks and form mode switching

---

## 15. Database Access Patterns

### ORM (Flask-SQLAlchemy)

Use for core entities like `User` and `DocumentationPage`:

> **YOUR CODE** — use these patterns in your own routes/helpers when working with ORM models.

```python
from app_db import User, db

# Query
user = User.query.filter_by(username="alice").first()

# Create
new_user = User(username="bob", email="bob@example.com")
new_user.set_password("secret")
new_user.set_role("editor")
db.session.add(new_user)
db.session.commit()
```

### Raw SQL (SQLAlchemy engine)

Use for feature-scoped tables, complex queries, or reporting:

> **YOUR CODE** — use these patterns in your own routes/helpers for custom tables.

```python
from app_db import get_sql_engine
from sqlalchemy import text

with get_sql_engine().connect() as conn:
    rows = conn.execute(text("SELECT * FROM my_table")).mappings().all()

with get_sql_engine().begin() as conn:  # auto-commits
    conn.execute(text("INSERT INTO my_table (col) VALUES (:val)"), {"val": "data"})
```

### DB URI

Always sourced from `app_db/config.py` via environment variables. Never hardcode credentials.

---

## 16. Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `DATABASE_URL` | Yes* | — | Full PostgreSQL connection string |
| `DB_USER` | Yes* | — | PostgreSQL user (alternative to `DATABASE_URL`) |
| `DB_PASSWORD` | Yes* | — | PostgreSQL password |
| `DB_HOST` | Yes* | — | PostgreSQL host |
| `DB_PORT` | Yes* | — | PostgreSQL port |
| `DB_NAME` | Yes* | — | PostgreSQL database name |
| `SECRET_KEY` | Prod | `dev-only-...` | Flask secret key (required in production) |
| `FLASK_PORT` | No | `5001` | Flask server port |
| `STREAMLIT_PORT` | No | `8501` | Streamlit server port |

\* Provide either `DATABASE_URL` **or** all five `DB_*` variables.

---

## Quick Reference — Decorator Cheat Sheet

> **YOUR CODE** — copy-paste these patterns into your own blueprint files.

```python
from flask_login import login_required
from flask_app.routes.permissions import role_required, admin_required

# Any logged-in user
@bp.route("/page")
@login_required
def page(): ...

# Only admins
@bp.route("/admin-page")
@login_required
@role_required("admin")
def admin_page(): ...

# Shortcut for admin-only
@bp.route("/admin-page")
@login_required
@admin_required()
def admin_page(): ...

# Editors, approvers, and admins
@bp.route("/editor-page")
@login_required
@role_required("editor", "approval1", "approval2", "admin")
def editor_page(): ...

# Custom flash message on denial
@bp.route("/secret")
@login_required
@role_required("admin", message="You cannot access this page.")
def secret(): ...
```

---

## Quick Reference — Template Cheat Sheet

> **YOUR CODE** — use these snippets in your own templates.

```html
<!-- CSRF token (required in every POST form) -->
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">

<!-- Show link to all logged-in users -->
{% if current_user.is_authenticated %}
<a href="...">Link</a>
{% endif %}

<!-- Show link only to specific roles -->
{% if current_user.role in ['editor', 'admin'] %}
<a href="...">Editor Link</a>
{% endif %}

<!-- Show link only to admins -->
{% if current_user.role == "admin" %}
<a href="...">Admin Link</a>
{% endif %}

<!-- Embed an internal tool in an iframe -->
<iframe src="{{ tool_url }}" style="width:100%; height:calc(100vh - 60px); border:none;"></iframe>
```
