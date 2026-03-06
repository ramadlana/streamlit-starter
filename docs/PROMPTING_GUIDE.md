# Prompting Guide — New Features

Use these prompt templates when asking an AI/agent to add features to this app. They reference [AGENTS.md](AGENTS.md) (in this folder) so the agent follows repo conventions and you get fewer fixes and less back-and-forth.

Replace the `<...>` placeholders with your specific feature description before sending.

---

## Master prompt (any feature)

Copy and paste, then fill in the placeholder:

```
New feature: <put your feature description here>.

Follow AGENTS.md strictly. Before coding:
1. If non-trivial: add or link a SPEC-* in SPECS.md and list files/routes/tables impacted.
2. Say which playbook you use: protected Flask route | full CRUD | Streamlit page.

Then implement. Must-do:
- Flask: new blueprint → import + register in flask_app/__init__.py; @login_required or @role_required as needed; url_for("blueprint.endpoint"); every POST form has csrf_token.
- CRUD: DB logic in app_db/<feature>.py (ORM or get_sql_engine per AGENTS §9); nav in templates/base.html if user-facing.
- Streamlit: new file under dashboard_pages/ with "import streamlit as st"; register in dashboard_app.py (st.Page + add to st.navigation).
- Templates: extend base.html, use base.css classes only ([FRAMEWORK_REFERENCE.md](FRAMEWORK_REFERENCE.md) — Design System), no inline styles.

Run compileall when done. Update README/AGENTS/DEPLOYMENT/FRAMEWORK_REFERENCE if routes or structure change.
```

---

## Short prompts (by feature type)

Use these when the feature type is clear. Replace only the placeholder.

### New protected Flask page

```
Add a protected Flask page: <put your page or feature here>.

Follow AGENTS.md §8 "Add a protected Flask route". Use @login_required, url_for, CSRF on forms. If new blueprint: import and register in flask_app/__init__.py. Extend base.html, base.css only.
```

### New CRUD feature

```
Add a CRUD feature: <put your CRUD feature here>.

Follow AGENTS.md §8 "Add a CRUD feature". Put DB in app_db/<feature>.py (raw SQL via get_sql_engine or ORM per §9). New blueprint → register in flask_app/__init__.py. Templates extend base.html; POST forms include csrf_token. Add nav in base.html if user-facing.
```

### New Streamlit page

```
Add a Streamlit page: <put your Streamlit page here>.

Follow AGENTS.md §8 "Add a Streamlit page". Create dashboard_pages/<name>.py with "import streamlit as st". In dashboard_app.py add st.Page(...) and add to st.navigation({...}). No new backend unless needed.
```

---

## Placeholder reference

| Placeholder | Use for | Example |
|-------------|---------|---------|
| `<put your feature description here>` | Master prompt; one-line summary | "Reports dashboard for editors" |
| `<put your page or feature here>` | Flask page | "Team roster view" |
| `<put your CRUD feature here>` | CRUD feature | "Project milestones" |
| `<put your Streamlit page here>` | Streamlit page | "Sales by region chart" |
| `<feature>` | In instructions: Python module name | `reports`, `milestones` |
| `<name>` | In instructions: Streamlit file name | `sales_regions.py` |

---

## See also

- [AGENTS.md](AGENTS.md) — Repo map, playbooks, route inventory, security rules
- [FRAMEWORK_REFERENCE.md](FRAMEWORK_REFERENCE.md) — Architecture, design system, auth, roles, adding pages (beginner-friendly)
- [CLEAN_FRAMEWORK.md](CLEAN_FRAMEWORK.md) — Remove all demo features for a minimal framework
- [SPECS.md](SPECS.md) — Spec-driven workflow for non-trivial changes
- [../README.md](../README.md) — Quick start, routes, project layout
