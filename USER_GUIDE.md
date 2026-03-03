# User Guide

This guide is for beginners who want to add features safely in this codebase.

## 1. Understand the flow first

- Flask handles authentication and protected pages.
- Streamlit UI is accessed through Flask after login.
- PostgreSQL stores users and feature data.

Main folders:
- `flask_app/routes/`: Flask route files
- `app_db/`: DB config, models, SQL engine/helpers
- `templates/`: HTML templates

## 2. Start the project

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set DB env vars:
```bash
export DB_USER=appuser
export DB_PASSWORD=strongpassword
export DB_HOST=127.0.0.1
export DB_PORT=5432
export DB_NAME=appdb
export SECRET_KEY=change-this-internal-secret
```

3. Create admin user:
```bash
python3 scripts/manage_admin.py create admin admin@example.com admin123
```

4. Run:
```bash
python3 run.py
```

## 3. Add a simple page (public + protected)

Create `flask_app/routes/reports.py`:

```python
from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint("reports", __name__)


@bp.route("/reports")
def reports_public():
    return render_template("reports_public.html")


@bp.route("/reports/secure")
@login_required
def reports_secure():
    return render_template("reports_secure.html")
```

Register it in `flask_app/__init__.py`:

```python
from flask_app.routes.reports import bp as reports_bp
...
app.register_blueprint(reports_bp)
```

Create `templates/reports_public.html`:

```html
{% extends "base.html" %}
{% block title %}Reports Public{% endblock %}
{% block content %}
<div class="card">
  <h1>Reports (Public)</h1>
  <p class="subtitle">No login required.</p>
</div>
{% endblock %}
```

Create `templates/reports_secure.html`:

```html
{% extends "base.html" %}
{% block title %}Reports Secure{% endblock %}
{% block content %}
<div class="card">
  <h1>Reports (Secure)</h1>
  <p class="subtitle">Login required.</p>
</div>
{% endblock %}
```

Optional nav links in `templates/base.html`:

```html
<a href="{{ url_for('reports.reports_public') }}">Reports</a>
{% if current_user.is_authenticated %}
<a href="{{ url_for('reports.reports_secure') }}">Secure Reports</a>
{% endif %}
```

## 4. Add a DB-backed page (full CRUD example)

Goal: add `/inventory` with create, list, edit, delete.

### Step A: Create DB helper

Create `app_db/inventory.py`:

```python
from sqlalchemy import text

from app_db import get_sql_engine


def ensure_inventory_table():
    with get_sql_engine().begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS inventory_items (
                    id BIGSERIAL PRIMARY KEY,
                    item_name VARCHAR(150) NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
        )


def get_inventory_items():
    ensure_inventory_table()
    with get_sql_engine().connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT id, item_name, quantity, created_at, updated_at
                FROM inventory_items
                ORDER BY id DESC
                """
            )
        )
        return rows.mappings().all()


def add_inventory_item(item_name: str, quantity: int):
    ensure_inventory_table()
    with get_sql_engine().begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO inventory_items (item_name, quantity)
                VALUES (:item_name, :quantity)
                """
            ),
            {"item_name": item_name, "quantity": quantity},
        )


def update_inventory_item(item_id: int, item_name: str, quantity: int) -> bool:
    ensure_inventory_table()
    with get_sql_engine().begin() as conn:
        updated = conn.execute(
            text(
                """
                UPDATE inventory_items
                SET item_name = :item_name,
                    quantity = :quantity,
                    updated_at = NOW()
                WHERE id = :item_id
                """
            ),
            {"item_id": item_id, "item_name": item_name, "quantity": quantity},
        )
        return updated.rowcount > 0


def delete_inventory_item(item_id: int) -> bool:
    ensure_inventory_table()
    with get_sql_engine().begin() as conn:
        deleted = conn.execute(
            text("DELETE FROM inventory_items WHERE id = :item_id"),
            {"item_id": item_id},
        )
        return deleted.rowcount > 0
```

### Step B: Create routes

Create `flask_app/routes/inventory.py`:

```python
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app_db.inventory import (
    add_inventory_item,
    delete_inventory_item,
    get_inventory_items,
    update_inventory_item,
)

bp = Blueprint("inventory", __name__)


@bp.route("/inventory")
@login_required
def inventory_page():
    items = get_inventory_items()
    return render_template("inventory.html", items=items)


@bp.route("/inventory/create", methods=["POST"])
@login_required
def inventory_create():
    item_name = (request.form.get("item_name") or "").strip()
    quantity_raw = (request.form.get("quantity") or "0").strip()

    if not item_name:
        flash("Item name is required.")
        return redirect(url_for("inventory.inventory_page"))

    try:
        quantity = int(quantity_raw)
    except ValueError:
        flash("Quantity must be a number.")
        return redirect(url_for("inventory.inventory_page"))

    add_inventory_item(item_name, quantity)
    flash("Item added.")
    return redirect(url_for("inventory.inventory_page"))


@bp.route("/inventory/edit/<int:item_id>", methods=["POST"])
@login_required
def inventory_edit(item_id):
    item_name = (request.form.get("item_name") or "").strip()
    quantity_raw = (request.form.get("quantity") or "0").strip()

    if not item_name:
        flash("Item name is required.")
        return redirect(url_for("inventory.inventory_page"))

    try:
        quantity = int(quantity_raw)
    except ValueError:
        flash("Quantity must be a number.")
        return redirect(url_for("inventory.inventory_page"))

    ok = update_inventory_item(item_id, item_name, quantity)
    flash("Item updated." if ok else "Item not found.")
    return redirect(url_for("inventory.inventory_page"))


@bp.route("/inventory/delete/<int:item_id>", methods=["POST"])
@login_required
def inventory_delete(item_id):
    ok = delete_inventory_item(item_id)
    flash("Item deleted." if ok else "Item not found.")
    return redirect(url_for("inventory.inventory_page"))
```

### Step C: Register blueprint

In `flask_app/__init__.py`:

```python
from flask_app.routes.inventory import bp as inventory_bp
...
app.register_blueprint(inventory_bp)
```

### Step D: Create template

Create `templates/inventory.html`:

```html
{% extends "base.html" %}
{% block title %}Inventory{% endblock %}
{% block content %}
<div class="card" style="max-width: 900px; width: 100%;">
  <h1>Inventory</h1>
  <p class="subtitle">DB-backed CRUD example</p>

  {% with messages = get_flashed_messages() %}
  {% if messages %}
  <div class="flash-messages">
    {% for message in messages %}
    <div class="flash-message">{{ message }}</div>
    {% endfor %}
  </div>
  {% endif %}
  {% endwith %}

  <form method="POST" action="{{ url_for('inventory.inventory_create') }}">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    <div class="form-group">
      <label>Item Name</label>
      <input type="text" name="item_name" required />
    </div>
    <div class="form-group">
      <label>Quantity</label>
      <input type="number" name="quantity" value="0" required />
    </div>
    <button class="btn" type="submit">Add Item</button>
  </form>

  <hr style="margin: 1.5rem 0; border-color: rgba(255,255,255,0.1);" />

  <table style="width: 100%; border-collapse: collapse;">
    <thead>
      <tr>
        <th style="text-align: left; padding: 8px;">ID</th>
        <th style="text-align: left; padding: 8px;">Item</th>
        <th style="text-align: left; padding: 8px;">Qty</th>
        <th style="text-align: left; padding: 8px;">Created</th>
        <th style="text-align: left; padding: 8px;">Updated</th>
        <th style="text-align: left; padding: 8px;">Actions</th>
      </tr>
    </thead>
    <tbody>
      {% for item in items %}
      <tr>
        <td style="padding: 8px;">{{ item.id }}</td>
        <td style="padding: 8px;">
          <form method="POST" action="{{ url_for('inventory.inventory_edit', item_id=item.id) }}" id="edit-{{ item.id }}">
            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
            <input type="text" name="item_name" value="{{ item.item_name }}" required />
          </form>
        </td>
        <td style="padding: 8px;">
          <input type="number" name="quantity" value="{{ item.quantity }}" required form="edit-{{ item.id }}" />
        </td>
        <td style="padding: 8px;">{{ item.created_at }}</td>
        <td style="padding: 8px;">{{ item.updated_at }}</td>
        <td style="padding: 8px; white-space: nowrap;">
          <button class="btn" type="submit" form="edit-{{ item.id }}" style="width:auto; margin-top:0;">Update</button>
          <form method="POST" action="{{ url_for('inventory.inventory_delete', item_id=item.id) }}" style="display:inline-block;" onsubmit="return confirm('Delete this item?');">
            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
            <button class="btn" type="submit" style="width:auto; margin-top:0; background:#f43f5e;">Delete</button>
          </form>
        </td>
      </tr>
      {% else %}
      <tr>
        <td colspan="6" style="padding: 8px;">No items yet.</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% endblock %}
```

### Step E: Add nav link (optional)

In `templates/base.html` under authenticated links:

```html
<a href="{{ url_for('inventory.inventory_page') }}">Inventory</a>
```

### Step F: Test

1. Run `python3 run.py`
2. Login
3. Open `http://127.0.0.1:5001/inventory`
4. Verify create, edit, and delete work

## 5. Auth behavior

- Login page: `/login`
- Signup page: `/signup`
- Logout: `/logout`
- `@login_required` routes redirect to login page automatically

## 6. Beginner checklist (before commit)

1. Blueprint imported + registered in `flask_app/__init__.py`
2. Route names match template `url_for(...)`
3. Template filename matches `render_template(...)`
4. `@login_required` added where needed
5. DB env vars configured
6. Quick syntax check passes:
```bash
python3 -m compileall -q app_db flask_app auth_server.py scripts models.py
```

## 7. Common mistakes

- `BuildError`: wrong blueprint or endpoint name in `url_for`
- 404 route: blueprint not registered
- DB runtime error: missing `DATABASE_URL` or `DB_*` env vars
- Unexpected logout/session reset: `SECRET_KEY` missing or changed
- Template not found: wrong template path/name
