# Design System — Internal Tool Starter Kit

This document defines HTML and CSS standards for the Flask-based internal tool framework. Use it when adding or changing pages so the repo stays a consistent, professional scaffolding for new apps.

---

## 1. Principles

- **Single stylesheet**: All styles live in `static/css/base.css`. Do not add new CSS files or inline `<style>` blocks in templates.
- **Extend base**: Every page extends `templates/base.html` and fills `{% block content %}` (and optionally `title`, `body_class`, `extra_css`).
- **Use design tokens**: Prefer CSS variables from `:root` (e.g. `var(--accent-color)`, `var(--radius)`) and existing utility/component classes instead of hardcoded colors or one-off styles.
- **No duplication**: Reuse existing classes (e.g. `btn`, `form-control`, `crud-panel`) rather than redefining the same look in templates.

---

## 2. Page Structure

### 2.1 Base template

- **Logo**: `.logo` in the navbar — default text is "Internal Tool". Change it in `base.html` when branding your app.
- **Flash messages**: Rendered once in `base.html` via `{% block flash_messages %}`. Child templates must **not** repeat flash markup; override the block only if a page needs a different placement or styling.
- **Scripts**: Nav toggle and `AppModal` are in `base.html`. Page-specific JS stays in the page template at the bottom of `{% block content %}`.

### 2.2 Body classes

Set `{% block body_class %}` for layout:

| Class | Use |
|-------|-----|
| *(none)* | Centered content (e.g. login card). |
| `content-top` | Full-width, top-aligned (CRUD, admin, list pages). |
| `docs-light` | Docs section: light background, left-aligned content. |
| `page-dashboard` | Home/dashboard: full-height iframe, no padding. |

Use a single class or space-separated list, e.g. `content-top page-dashboard` for the dashboard.

### 2.3 Blocks

- **title**: Page title (browser tab). Keep short, e.g. "Login", "Admin Panel".
- **content**: Main HTML for the page.
- **extra_css**: Optional; only for extra stylesheets (e.g. Quill). Do not put inline CSS here.
- **body_class**: Optional; see above.
- **flash_messages**: Optional override; usually leave as default.

---

## 3. Components and Classes

### 3.1 Buttons

- **Primary**: `btn btn-primary` (or `btn` alone; primary is default for submit).
- **Secondary / cancel**: `btn btn-secondary`.
- **Ghost**: `btn btn-ghost`.
- **Danger**: `btn btn-danger`.
- **Sizing**: `btn-small` for compact; `w-auto` for non-full-width, `w-100` for full width.

Use these instead of inline `style="background: ..."`.

### 3.2 Forms

- **Group**: `form-group` wraps label + control.
- **Label**: `form-label` on `<label>`; use `for` and matching `id` on inputs.
- **Inputs**: `form-control` on `<input>`, `<textarea>`, `<select>`; add `form-select` on `<select>`.
- **No inline styles** on form elements; use utility classes (e.g. `mt-2`, `d-none`).

### 3.3 Layout and utilities

- **Flex**: `d-flex`, `justify-content-between`, `align-items-center`, `gap-3`, etc. (see `base.css` and FRAMEWORK_GUIDE § Base CSS).
- **Spacing**: `m-0`, `mt-2`, `mb-3`, `p-4`, etc.
- **Text**: `text-muted`, `text-center`, `text-danger`, `small`.
- **Visibility**: `d-none` to hide (toggle via JS with `classList.add/remove('d-none')`).

### 3.4 CRUD pages

- **Container**: `crud-container` (or `admin-container` for admin).
- **Header**: `crud-header` with `h1` and `p.subtitle`.
- **Panel**: `crud-panel` for each card; panel title: `h3.crud-panel-title`.
- **Table**: `crud-table-wrapper` > `table.crud-table`; action cells use `.actions` with `btn btn-small btn-ghost` / `btn btn-small btn-danger`.
- **Form**: `form-compact` with `form-group`, `form-label`, `form-control`; submit `btn btn-primary`.

### 3.5 Modals

- Use the macro: `{% from "components/modal.html" import modal %}` and `{% call modal('id') %}...{% endcall %}`.
- Content: `app-modal-content`, `app-modal-actions`, `app-modal-danger-icon`, `app-modal-body-muted` (all in `base.css`).
- Open/close via `AppModal.open('id')` and `AppModal.close('id')`.

### 3.6 Alerts and flash

- **Success / error in content**: Prefer `alert alert-success` or `alert alert-danger` for in-page messages.
- **Flash**: Styled automatically in base; uses `.flash-message` inside `.flash-messages`. For error emphasis, backend can flash and front-end will show it in the standard block.

---

## 4. Naming Conventions

- **CSS**: Use kebab-case (e.g. `crud-panel-title`, `app-modal-actions`). Prefix feature-specific blocks (e.g. `docs-*`, `crud-*`, `admin-*`) to avoid clashes.
- **Templates**: `snake_case.html` for pages; `components/modal.html` for shared partials.
- **IDs**: Use kebab-case or snake_case for form fields and JS hooks (e.g. `item-name`, `edit_username`).

---

## 5. Checklist for New Pages

1. Extend `base.html` and set `{% block title %}` and, if needed, `{% block body_class %}`.
2. Use only classes from `base.css`; no inline styles or new `<style>` tags.
3. All POST forms include `{% csrf_token() %}` in a hidden input.
4. Buttons use `btn` + variant; forms use `form-group`, `form-label`, `form-control`.
5. Do not add a duplicate flash block; base already shows flashed messages.
6. For modals, use `components/modal.html` and `AppModal`.

---

## 6. References

- **FRAMEWORK_GUIDE.md** — Section "Base CSS & Style Guide" for a full list of utility and component classes.
- **AGENTS.md** — Repo map, routes, and change playbooks.
- **static/css/base.css** — Single source of truth; sections are commented (e.g. "CRUD", "Admin", "Dashboard").
