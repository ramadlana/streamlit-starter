# Clean Framework Guide — Remove All Demo Features

This guide removes **every demo/example feature** so you have a minimal framework to build your own. You will remove:

| Category | Removed |
|----------|---------|
| **Flask demo CRUD** | `/example-crud`, `/dummydata-crud` (blueprints, routes, templates, `app_db/example_crud.py`) |
| **Docs** | `/docs` and all docs routes (blueprint, templates, `app_db/docs.py`, `app_db/docs_attachments.py`, `DocumentationPage` model) |
| **Streamlit iframe page** | `/iframe-app-streamlit` (blueprint, template) |
| **Streamlit example pages** | Entire "Example" group (Basic Page, Map, Components, Sales Dashboard, PSQL Dummydata, PSQL Pagination, etc.) |

**After cleanup you keep:** Flask (home, auth, admin), Streamlit (single “Home” page that renders README), app_db (User, roles, app_settings, engine), and a minimal nav/home so you can add your own features.

---

## Checklist overview

1. [Flask `__init__.py`](#1-flask-__init__py) — Unregister and remove imports for example_crud, dummydata_crud, docs, iframe_app_streamlit.
2. [Nav and home templates](#2-nav-and-home-templates) — Remove all demo links from `base.html` and `home.html`.
3. [Delete Flask route files](#3-delete-flask-route-files) — example_crud, dummydata_crud, docs, iframe_app_streamlit.
4. [Delete Flask templates](#4-delete-flask-templates) — example_crud, dummydata_crud, docs_*, iframe_app_streamlit.
5. [app_db](#5-app_db) — Remove example_crud, docs, docs_attachments; remove `DocumentationPage` from models and `app_db/__init__.py`.
6. [Streamlit](#6-streamlit) — Remove `dashboard_pages/example/` and `dashboard_pages/pages/`; simplify `dashboard_app.py` to only the Home page.
7. [Scripts](#7-scripts) — Remove or keep `docs_attachments_housekeeping.py` (optional).
8. [Documentation](#8-documentation) — Update README, docs/AGENTS, docs/FRAMEWORK_REFERENCE, docs/PROMPTING_GUIDE.
9. [Optional DB cleanup](#9-optional-database-cleanup) — Drop tables that are no longer used.

---

## 1. Flask `flask_app/__init__.py`

**Remove these imports** (at the top):

```python
from flask_app.routes.example_crud import bp as example_crud_bp
from flask_app.routes.dummydata_crud import bp as dummydata_crud_bp
from flask_app.routes.docs import bp as docs_bp
from flask_app.routes.iframe_app_streamlit import bp as iframe_app_streamlit_bp
```

**Remove these registrations** (inside `create_app()`):

```python
app.register_blueprint(example_crud_bp)
app.register_blueprint(dummydata_crud_bp)
app.register_blueprint(docs_bp)
app.register_blueprint(iframe_app_streamlit_bp)
```

Keep: `home_bp`, `auth_bp`, `admin_bp`.

---

## 2. Nav and home templates

### 2.1 `templates/base.html`

- Remove the **Iframe App Streamlit** link:  
  `<a href="{{ url_for('iframe_app_streamlit.iframe_app_streamlit') }}">Iframe App Streamlit</a>`
- Remove the **Docs** link:  
  `<a href="{{ url_for('docs.docs_index') }}">Docs</a>`
- Remove the **Editor Menu** dropdown entirely (the `<div class="nav-dropdown">` that contains "Editor Menu" with Example CRUD and Dummydata CRUD). If you prefer to keep the dropdown for future features, only remove the two `<a>` tags inside the menu.

Result: authenticated nav should have only **Home** (and **Admin Panel** for admins), plus the user dropdown and Logout.

### 2.2 `templates/home.html`

- **Need help?** strip: remove or change the line that says “Check the Docs” so it no longer uses `url_for('docs.docs_index')`.
- **News** section: remove the news item that links to “New documentation hub” / `url_for('docs.docs_index')`.
- **Apps** section:
  - Remove the **Dashboard** card that links to `url_for('iframe_app_streamlit.iframe_app_streamlit')`.
  - Remove the **Docs** card that links to `url_for('docs.docs_index')`.
  - Remove the **Example CRUD** and **Dummydata** cards (the two inside `{% if can_show_editor_menu %}`).

You can leave the Apps grid structure and add your own cards later, or simplify the section.

---

## 3. Delete Flask route files

Delete these files:

- `flask_app/routes/example_crud.py`
- `flask_app/routes/dummydata_crud.py`
- `flask_app/routes/docs.py`
- `flask_app/routes/iframe_app_streamlit.py`

Keep: `auth.py`, `admin.py`, `home.py`, `permissions.py`, and `routes/__init__.py`.

---

## 4. Delete Flask templates

Delete these templates:

- `templates/example_crud.html`
- `templates/dummydata_crud.html`
- `templates/docs_index.html`
- `templates/docs_view.html`
- `templates/docs_editor.html`
- `templates/iframe_app_streamlit.html`

Keep: `base.html`, `home.html`, `login.html`, `signup.html`, `admin.html`, `change_password.html`, `components/modal.html`.

---

## 5. app_db

### 5.1 Delete modules

- Delete `app_db/example_crud.py`
- Delete `app_db/docs.py`
- Delete `app_db/docs_attachments.py`

### 5.2 Edit `app_db/__init__.py`

- Remove: `from app_db.example_crud import ensure_example_crud_table`
- Remove: `from app_db.docs import (...)` (all docs-related imports)
- Remove: `from app_db.models import DocumentationPage, User` → use only `from app_db.models import User`
- From `__all__`, remove: `"ensure_example_crud_table"`, `"DocumentationPage"`, `"get_document_by_id"`, `"get_document_by_slug"`, `"list_documents"`, `"create_or_update_document"`

### 5.3 Edit `app_db/models.py`

- Remove the **`DocumentationPage`** model class entirely (the class with `__tablename__ = "documentation_pages"`).

Keep: `User` and any other models you add.

---

## 6. Streamlit

### 6.1 Delete example and unused pages

- Delete the entire directory **`dashboard_pages/example/`** (all files inside it).
- Delete the directory **`dashboard_pages/pages/`** if it exists (e.g. `overview.py` is not in the nav; removing it keeps the framework clean).

Keep: **`dashboard_pages/home.py`** (minimal page, e.g. rendering README).

### 6.2 Simplify `dashboard_app.py`

Replace the page definitions and navigation so only the Home page remains, for example:

```python
import streamlit as st

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# Page Definitions — add your own st.Page(...) here
home_page = st.Page("dashboard_pages/home.py", title="Home", icon=":material/home:")

# Navigation — add your own groups and pages
pg = st.navigation(
    {
        "Main Menu": [home_page],
    }
)

st.set_page_config(page_title="App Name", page_icon=":material/home:")
pg.run()
```

Remove all references to: `basic_page`, `map_page`, `streamlit_components_page`, `sales_dashboard_page`, `table_postgresql_page`, `table_pagination_postgresql_page`, and the "Example" group.

---

## 7. Scripts

- **`scripts/docs_attachments_housekeeping.py`** — Only used by the docs feature. You can **delete** it for a clean framework, or keep it if you plan to reuse similar logic.

Keep: `scripts/manage_admin.py`, `scripts/kill_ports.py`.

---

## 8. Documentation

Update these so they no longer describe removed features:

- **README.md** (root) — Routes section: remove mentions of `/example-crud`, `/dummydata-crud`, `/docs`, `/iframe-app-streamlit`. Database notes: remove `example_crud_items`, `documentation_pages` / docs. Documentation table: links point to `docs/` (e.g. docs/CLEAN_FRAMEWORK.md).
- **AGENTS.md** — Repo map: remove example_crud, dummydata_crud, docs, iframe_app_streamlit from routes and templates; remove app_db docs/example_crud; update route inventory and read-first order so they don’t reference removed blueprints.
- **FRAMEWORK_REFERENCE.md** — Remove or replace examples that use docs, iframe_app_streamlit, example_crud, dummydata_crud (e.g. Editor Menu, docs routes). Keep the generic “add a Flask page / CRUD / Streamlit page” playbooks.
- **PROMPTING_GUIDE.md** — No change needed (it references AGENTS.md and playbooks; those still apply).

---

## 9. Optional: database cleanup

After the app no longer uses the demo features:

- **`example_crud_items`** — No longer created or used. Optional:  
  `DROP TABLE IF EXISTS example_crud_items;`
- **`documentation_pages`** — No longer used after removing docs and `DocumentationPage`. Optional:  
  `DROP TABLE IF EXISTS documentation_pages;`
- **`dummydata`** — Only used by the removed Streamlit example pages. Optional:  
  `DROP TABLE IF EXISTS dummydata;`

Run these only if you are sure you don’t need the data.

---

## 10. Verify

1. **Compile:**  
   `python3 -m compileall -q app_db flask_app auth_server.py scripts`

2. **Run:**  
   `python3 run.py`

3. **Check:**
   - Login works; home page loads.
   - Nav shows only Home (and Admin for admin users); no Docs, Iframe App Streamlit, Editor Menu (or Editor Menu with no demo links).
   - `/example-crud`, `/dummydata-crud`, `/docs`, `/iframe-app-streamlit` return 404.
   - Streamlit sidebar shows only “Home” (or whatever you left in Main Menu).

---

## Summary: what you have after cleanup

| Layer | Kept |
|-------|------|
| **Flask** | home (`/`), auth (login, signup, logout, change-password, auth-check), admin |
| **Streamlit** | One “Home” page (e.g. `dashboard_pages/home.py`) |
| **app_db** | `User`, `db`, `get_sql_engine`, `build_database_uri`, `user_roles`, `app_settings`, `engine`, `config`, `base`, `models` (without `DocumentationPage`) |
| **Templates** | base, home, login, signup, admin, change_password, components/modal |
| **Scripts** | manage_admin, kill_ports |

From here you can add your own routes, CRUD features, and Streamlit pages using [AGENTS.md](AGENTS.md) and [PROMPTING_GUIDE.md](PROMPTING_GUIDE.md). (All in this `docs/` folder; see also [../README.md](../README.md).)
