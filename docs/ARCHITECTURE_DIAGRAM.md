# Starter Kit Architecture — Mermaid Diagrams

How the Flask auth gateway + Streamlit dashboard boilerplate works.

---

## 1. Runtime & process layout

```mermaid
flowchart TB
    subgraph entry["Entry point"]
        RUN["run.py"]
    end

    RUN --> cleanup["cleanup_ports()"]
    RUN --> config["get_config_ports()\nFLASK_PORT / STREAMLIT_PORT"]
    RUN --> streamlit_cmd["Streamlit subprocess"]
    RUN --> flask_cmd["Flask subprocess\n(auth_server.py)"]

    subgraph processes["Two processes"]
        subgraph flask["Flask app (e.g. :5001)"]
            AUTH["auth_server.py"]
            CREATE["create_app()"]
            AUTH --> CREATE
        end
        subgraph streamlit["Streamlit app (e.g. :8501)"]
            DASH["dashboard_app.py"]
            PAGES["dashboard_pages/*.py"]
            DASH --> PAGES
        end
    end

    streamlit_cmd --> streamlit
    flask_cmd --> flask

    RUN -.->|"--prod"| basePath["Streamlit baseUrlPath\n/dashboard-app/"]
```

- **run.py** starts both servers and (in `--prod`) configures Streamlit for the `/dashboard-app/` proxy path.
- **Flask** is the auth/session gateway; **Streamlit** is the dashboard UI, either on its own port (dev) or under Nginx (prod).

---

## 2. Request flow: user → login → app

```mermaid
sequenceDiagram
    participant U as User / Browser
    participant F as Flask (auth gateway)
    participant DB as PostgreSQL
    participant S as Streamlit

    U->>F: GET /
    alt not logged in
        F->>U: Redirect /login
        U->>F: GET /login
        F->>U: login form
        U->>F: POST /login (username, password)
        F->>DB: User lookup + check_password
        DB-->>F: user
        F->>F: login_user() → session
        F->>U: Redirect /
    end

    F->>U: 200 home.html (or redirect)

    opt Open dashboard
        U->>F: GET /iframe-app-streamlit
        F->>F: @login_required
        F->>U: 200 iframe_app_streamlit.html
        note over U: iframe src = streamlit_url
        U->>S: GET streamlit_url (dev: :8501, prod: /dashboard-app/)
        S->>U: Streamlit app (multipage)
    end
```

- All protected routes go through Flask; session is Flask-Login.
- Streamlit is loaded inside an iframe; in dev the iframe points to `http://localhost:8501`, in prod to `/dashboard-app/`.

---

## 3. Flask app structure (create_app)

```mermaid
flowchart LR
    subgraph create_app["create_app() in flask_app/__init__.py"]
        config["Config\nSECRET_KEY, DB URI"]
        ext["Extensions\n(db, csrf, login_manager)"]
        ctx["Context processors\n(csrf_token, editor_menu, allow_signup)"]
        err["CSRF error handler"]
        blueprints["Register blueprints"]
        init_db["db.create_all()\nensure_user_role_column\nensure_app_settings_table"]
    end

    config --> ext
    ext --> ctx
    ctx --> err
    err --> blueprints
    blueprints --> init_db
```

```mermaid
flowchart TB
    subgraph blueprints["Blueprints"]
        home["home\n/"]
        auth["auth\n/login, /signup, /logout,\n/change-password, /auth-check"]
        admin["admin\n/admin, /admin/settings\n/admin/add|edit|delete"]
        example_crud["example_crud\n/example-crud/*"]
        dummydata_crud["dummydata_crud\n/dummydata-crud/*"]
        docs["docs\n/docs, /docs/<slug>\n/docs/editor, /docs/upload-image\n/docs/attachments/*"]
        iframe["iframe_app_streamlit\n/iframe-app-streamlit"]
    end

    create_app --> blueprints
```

- One Flask app; blueprints provide routes. Auth is enforced with `@login_required` and role checks where needed.

---

## 4. Data & database

```mermaid
flowchart TB
    subgraph app_db["app_db"]
        config["config.py\nbuild_database_uri()"]
        base["base.py\n(db)"]
        models["models.py\nUser, DocumentationPage"]
        engine["engine.py\nget_sql_engine()"]
        roles["user_roles.py"]
        settings["app_settings.py"]
        docs_db["docs.py"]
        example["example_crud.py"]
    end

    subgraph usage["Usage"]
        routes["Flask routes"]
        scripts["scripts/"]
    end

    config --> base
    config --> engine
    base --> models
    models --> roles
    base --> settings
    base --> docs_db
    base --> example

    routes --> app_db
    scripts --> app_db

    app_db --> PG[(PostgreSQL)]
```

- **ORM** (Flask-SQLAlchemy): `User`, `DocumentationPage`; core CRUD and auth.
- **Raw SQL** (engine from `app_db.config`): reporting, complex queries, feature tables (e.g. dummydata).
- DB URI comes only from `app_db/config.py` (env: `DATABASE_URL` or `DB_*`).

---

## 5. Streamlit multipage navigation

```mermaid
flowchart TB
    subgraph streamlit_app["dashboard_app.py"]
        nav["st.navigation()"]
        home_p["Home"]
        basic["Basic Page"]
        map_p["Map Page"]
        components["Streamlit Components"]
        sales["Sales Dashboard"]
        table["PSQL Dummydata"]
        table_pag["PSQL Pagination Table"]
    end

    nav --> Main["Main Menu"]
    nav --> Example["Example"]

    Main --> home_p
    Example --> basic
    Example --> components
    Example --> map_p
    Example --> sales
    Example --> table
    Example --> table_pag

    home_p --> home_file["dashboard_pages/home.py"]
    basic --> basic_file["dashboard_pages/example/basic.py"]
    table --> table_file["dashboard_pages/example/table-postgresql-page.py"]
```

- Streamlit runs as a separate process; pages live under `dashboard_pages/`. Business logic and DB access stay in `app_db`/Flask; Streamlit focuses on UI.

---

## 6. Dev vs prod (Streamlit URL)

```mermaid
flowchart LR
    subgraph dev["Development"]
        U1[User]
        F1[Flask :5001]
        S1[Streamlit :8501]
        U1 --> F1
        U1 --> S1
        F1 -->|iframe src| S1
    end

    subgraph prod["Production (--prod)"]
        U2[User]
        Nginx[Nginx]
        F2[Flask]
        S2[Streamlit]
        U2 --> Nginx
        Nginx --> F2
        Nginx -->|/dashboard-app/| S2
        F2 -->|iframe src /dashboard-app/| Nginx
    end
```

- **Dev:** User hits Flask; Flask serves HTML with an iframe to `http://localhost:STREAMLIT_PORT`. User (or iframe) talks to Streamlit on that port.
- **Prod:** Nginx fronts both; Streamlit is mounted at `/dashboard-app/`; Flask serves pages that embed iframe `src="/dashboard-app/"`.

---

## Summary

| Layer            | Responsibility                                      |
|-----------------|------------------------------------------------------|
| **run.py**      | Start Flask + Streamlit; port cleanup; prod base path |
| **Flask**       | Auth (Flask-Login), CSRF, session, all HTML routes   |
| **Streamlit**   | Dashboard UI (multipage), no auth (gated by Flask)   |
| **app_db**      | PostgreSQL: ORM (User, docs) + raw SQL helpers      |
| **Templates**   | Jinja; base.html; CSRF on every POST form           |

All access to the app is through Flask first; the dashboard is shown via an iframe to Streamlit (direct in dev, via `/dashboard-app/` in prod).
