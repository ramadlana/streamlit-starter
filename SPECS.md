# SPECS.md

Shared, structured delivery specs for this repository.

Use this file to plan work before coding, keep team decisions visible, and verify implementation against explicit acceptance criteria.

## 1) How To Use This File

For each meaningful change:
1. Add a new spec section using the template below.
2. Keep status updated as work progresses.
3. Record verification evidence before closing.
4. If scope changes, update the spec first, then code.

If a change is tiny (docs typo, rename, comment-only), you can skip full spec details but still include a short verification note in PR/commit context.

---

## 2) Spec Template

Copy this block for each new initiative.

```md
## SPEC-<id>: <short title>

### Metadata
- Owner:
- Reviewers:
- Status: Draft | In Progress | In Review | Done | Blocked
- Priority: P0 | P1 | P2 | P3
- Target date:
- Related files:

### Problem Statement
What is broken/missing today? Why does it matter?

### Goals
- Goal 1
- Goal 2

### Non-Goals
- Explicitly out of scope item 1
- Explicitly out of scope item 2

### Constraints
- Technical constraints
- Security/compliance constraints
- Backward-compatibility constraints

### Current State Notes
- Relevant route/DB/template/runtime behavior
- Existing gotchas or dependencies

### Proposed Design
#### API / Route changes
- New or changed endpoints
- Auth requirements

#### Data model / SQL changes
- New tables/columns/indexes
- Migration/backfill notes

#### UI / Template changes
- New pages/forms/actions
- CSRF and authorization behavior

#### Streamlit changes (if any)
- New pages/navigation
- Data access patterns

### Implementation Plan
1. Step 1
2. Step 2
3. Step 3

### Acceptance Criteria
- [ ] Criterion 1 (observable behavior)
- [ ] Criterion 2 (security/permission behavior)
- [ ] Criterion 3 (failure mode or edge case)

### Verification Plan
- Commands to run
- Manual checks to perform
- Negative tests (unauthorized/invalid input)

### Risks and Mitigations
- Risk 1 -> mitigation
- Risk 2 -> mitigation

### Rollback Plan
How to safely revert if deploy causes issues.

### Change Log
- YYYY-MM-DD: <decision or scope update>

### Verification Evidence
- Command output summary:
- Manual test summary:
- Open follow-ups:
```

---

## 3) Verification Baseline (This Repo)

Unless the spec defines stricter checks, use at least:

```bash
python3 -m compileall -q app_db flask_app auth_server.py scripts models.py
```

Add relevant checks based on touched areas:
- Routes/templates changed: verify route renders, nav link works, form includes CSRF token.
- Auth/admin changed: verify anonymous/user/admin permission paths.
- Raw SQL changed: verify query executes with expected columns and error handling.
- Streamlit changed: verify page registration and app startup.

---

## 4) Active Specs

> Add new specs below this line.

## SPEC-2026-03-05-docs-platform: Built-in Documentation Platform

### Metadata
- Owner: Codex
- Reviewers: N/A
- Status: Done
- Priority: P1
- Target date: 2026-03-05
- Related files: `app_db/models.py`, `app_db/docs.py`, `app_db/__init__.py`, `flask_app/routes/docs.py`, `flask_app/__init__.py`, `templates/docs_index.html`, `templates/docs_view.html`, `templates/docs_editor.html`, `templates/base.html`, `static/css/docs.css`

### Problem Statement
The app does not have an internal documentation workspace for operational runbooks and knowledge base pages. Users need a built-in editor and reader with tagging, slug URLs, and image paste workflow that persists text in PostgreSQL while storing image assets on disk.

### Goals
- Add a login-protected documentation feature with index, viewer, editor, and tag filtering routes.
- Provide Quill.js editor with simplified toolbar, limited font options, and readable long-form typography.
- Support clipboard screenshot/image paste upload to Flask endpoint and embed as URL images (not base64).

### Non-Goals
- Document version history or approval workflows.
- External object storage integration (S3/GCS).

### Constraints
- Keep routes in `flask_app/routes/docs.py`.
- Keep DB logic in `app_db/docs.py`.
- Use ORM for core entity persistence; use raw SQL for feature helper/reporting query paths.
- Use PostgreSQL only, no SQLite.
- All protected views use `@login_required`.
- All HTML POST forms include CSRF hidden token.

### Current State Notes
- Existing app has auth, admin, and CRUD feature blueprints only.
- `db.create_all()` runs in app factory; adding ORM models will create missing tables.
- Base template already provides nav and global styles.

### Proposed Design
#### API / Route changes
- Add `docs` blueprint with:
- `GET /docs`: document index with search by title/slug and tag chips.
- `GET /docs/<slug>`: read page by slug.
- `GET|POST /docs/editor/<id>`: create/update page (`id=0` creates new).
- `GET /docs/tag/<tag>`: list/filter by tag.
- `POST /docs/upload-image`: accept pasted image file and return JSON URL for Quill embed.
- Require login for all docs routes.

#### Data model / SQL changes
- Add ORM model `DocumentationPage` (`id`, `title`, `slug`, `content_html`, `summary`, `tags_csv`, `created_by`, timestamps).
- Add unique index on slug and index on created/updated timestamp through ORM.
- Add `app_db/docs.py` helpers:
- ORM helpers for get/create/update and slug normalization.
- Raw SQL helper for tag filtering/index listing.

#### UI / Template changes
- Add docs index, viewer, and editor templates.
- Add docs-specific stylesheet with centered 720px content column, 18px base size, 1.7 line-height.
- Configure Quill toolbar for headers/basic formatting/lists/links/images/code-block/font selector.
- Whitelist fonts to `mirza` and `roboto` in Quill config; use CSS to style reading surface default with Aref Ruqaa.
- Include tag input for comma-separated tags.
- Include hidden CSRF token in editor POST form.

#### Streamlit changes (if any)
- None.

### Implementation Plan
1. Add spec entry and define acceptance criteria.
2. Implement ORM model and DB helper module for docs and tag filtering.
3. Implement docs blueprint routes including upload endpoint and slug routing.
4. Implement templates/CSS/JS for docs index, view, and Quill editor UX.
5. Register blueprint and nav link; run compile verification.
6. Update this spec with verification evidence and mark done.

### Acceptance Criteria
- [x] `/docs`, `/docs/<slug>`, `/docs/editor/<id>`, and `/docs/tag/<tag>` routes exist and are login protected.
- [x] Docs content persists in PostgreSQL via ORM model, and tag filter/list helper uses raw SQL in `app_db/docs.py`.
- [x] Editor uses Quill with simplified toolbar including font selector limited to Mirza and Roboto.
- [x] Reader/editor typography uses centered layout (~720px max), base font size 18px, and line-height 1.7 with Aref Ruqaa as default reading font.
- [x] Pasted image workflow uploads image to `/docs/upload-image`, stores under `uploads/attachments/docs`, and embeds URL image (not base64) into editor content.
- [x] Editor POST form contains CSRF hidden input.
- [x] Navigation includes link to docs index for authenticated users.
- [x] New docs uploads are stored under `uploads/attachments/docs`.
- [x] Existing `/docs/attachments/<filename>` URLs remain readable after path migration.
- [x] Housekeeping can identify orphaned attachments (not referenced by any docs content) and support safe cleanup workflow.
- [x] Housekeeping is runnable from CLI and from an admin-only in-app action.
- [x] Admin can delete docs from `/docs` using a modal confirmation flow.
- [x] Docs authorization enforces read-only access for `viewer`, while `editor`, `approval1`, `approval2`, and `admin` can create/edit/delete docs.

### Verification Plan
- Run:
- `python3 -m compileall -q app_db flask_app auth_server.py scripts models.py`
- Manual checks:
- Access control redirects anonymous users from docs routes to login.
- Create document via editor (`/docs/editor/0`), verify slug URL render at `/docs/<slug>`.
- Paste image into editor, verify file appears on disk and inserted image uses URL path.
- Filter by tag route and confirm expected documents shown.
- Confirm no base64 image payload saved in document HTML.

### Risks and Mitigations
- Risk: Quill pasted image handling could still insert base64 before upload.
- Mitigation: Intercept paste event and replace with upload workflow + URL embed.
- Risk: Filename/path injection via upload.
- Mitigation: Use `secure_filename`, allowed image MIME/extension checks, generated UUID names.

### Rollback Plan
Revert docs blueprint registration and docs-related files; remove `DocumentationPage` ORM class. Existing unrelated routes remain unaffected.

### Change Log
- 2026-03-05: Created initial implementation spec and scoped routes/data/UI/upload behavior.
- 2026-03-05: Implemented docs ORM/entity helpers, docs blueprint routes, Quill editor templates, and docs nav integration.
- 2026-03-05: Refined docs reader/editor visual design to a more Medium-like experience (lighter, less boxed, improved spacing/typography/actions).
- 2026-03-05: Expanded docs search to match content body and rank title/slug matches above content-only matches.
- 2026-03-05: Updated docs index cards to show title, updated date, and a short 10-word content preview.
- 2026-03-05: Expanded scope to include docs attachments housekeeping and storage path migration from `uploads/attachments/changemanagement` to `uploads/attachments/docs`.
- 2026-03-05: Implemented shared orphan-attachment cleanup service, admin docs housekeeping endpoint, and CLI housekeeping script with dry-run/apply modes.
- 2026-03-05: Expanded docs index admin controls to include document deletion with modal confirmation.
- 2026-03-05: Expanded docs role-based permissions: viewer read-only, non-viewer roles can create/edit/delete docs.

### Verification Evidence
- Command output summary: `python3 -m compileall -q app_db flask_app auth_server.py scripts models.py` completed successfully with exit code 0.
- Manual test summary: Code-level verification completed for required route definitions, CSRF form token presence, Quill font whitelist config, image paste upload path (`uploads/attachments/docs`), URL image embedding workflow, updated Medium-like reader/editor template + CSS structure, search ranking logic (title/slug matches ranked above content-only matches), docs index card preview extraction (10-word short content from summary/content), attachment housekeeping logic (orphan detection + admin/CLI entrypoints), admin docs deletion flow wiring (modal), and role-based docs permissions (`viewer` read-only; `editor`/`approval1`/`approval2`/`admin` can create/edit/delete). Live browser/manual interaction was not executed in this run.
- Open follow-ups: Perform browser validation of housekeeping action behavior in a running PostgreSQL-backed environment and confirm expected orphan list before first apply run.

## SPEC-2026-03-05-user-roles: Expand User Roles With Backward-Compatible Admin Behavior

### Metadata
- Owner: Codex
- Reviewers: N/A
- Status: Done
- Priority: P1
- Target date: 2026-03-05
- Related files: `app_db/models.py`, `app_db/user_roles.py`, `app_db/__init__.py`, `flask_app/__init__.py`, `flask_app/routes/admin.py`, `templates/admin.html`, `scripts/manage_admin.py`

### Problem Statement
The app currently supports only admin/non-admin behavior through `is_admin`. New business roles are required: `viewer`, `editor`, `approval1`, `approval2`, and `admin`. This must not break existing admin behavior or existing code paths that rely on `is_admin`.

### Goals
- Add explicit role support with allowed values `viewer|editor|approval1|approval2|admin`.
- Preserve current admin access behavior by keeping `is_admin` semantics intact.
- Allow admin users to view/update role values from the admin panel and CLI admin script output.

### Non-Goals
- Implement fine-grained authorization by role for each feature route.
- Replace/remove existing `is_admin` checks in the entire codebase.

### Constraints
- PostgreSQL only.
- Backward compatibility for existing user rows and existing `is_admin` logic.
- Keep admin rights behavior stable for existing flows.

### Current State Notes
- `User` model currently has `is_admin` but no role field.
- Existing admin routes/forms post an `is_admin` checkbox.
- Existing DBs may already have a populated `user` table without a `role` column.

### Proposed Design
#### API / Route changes
- Keep admin endpoints unchanged (`/admin/add`, `/admin/edit/<id>`), but extend payload with role select.
- Add route-side normalization to accept either role field (new) or `is_admin` checkbox (legacy form compatibility).

#### Data model / SQL changes
- Add `role` column on `User` model.
- Add startup helper to ensure role column exists in existing DBs using `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`.
- Backfill role values for existing rows:
- `is_admin = true` -> `role='admin'`
- null/empty role -> `role='viewer'`
- Keep `is_admin` synchronized from role (`role == 'admin'`).

#### UI / Template changes
- Admin table role badge shows normalized role.
- Add role select in add/edit user modals with all five roles.

### Implementation Plan
1. Add spec entry and define compatibility approach.
2. Implement role constants/normalization and DB column ensure/backfill helper.
3. Update `User` model and app startup initialization.
4. Update admin route logic + template role controls.
5. Update `scripts/manage_admin.py` list/create behavior for role.
6. Verify compile and record evidence.

### Acceptance Criteria
- [x] System supports roles: `viewer`, `editor`, `approval1`, `approval2`, `admin`.
- [x] Existing admin checks (`is_admin`) continue to work without behavioral regressions.
- [x] Existing databases without `role` column are auto-updated safely on startup.
- [x] Admin panel can assign/edit role for users.
- [x] `scripts/manage_admin.py` output includes role and create flow sets admin role correctly.

### Verification Plan
- Run:
- `python3 -m compileall -q app_db flask_app auth_server.py scripts models.py`
- Manual checks:
- Start app against existing DB and confirm startup does not fail.
- Open admin panel, create/edit user role, verify persistence.
- Confirm admin role still grants admin panel access.

### Risks and Mitigations
- Risk: Existing DB missing role column causes runtime errors.
- Mitigation: startup `ALTER TABLE IF NOT EXISTS` + backfill.
- Risk: role/is_admin drift.
- Mitigation: normalize role and explicitly sync `is_admin` during create/edit/backfill.

### Rollback Plan
Revert role-related model/route/template changes and startup role ensure helper. Existing `is_admin` behavior remains available.

### Change Log
- 2026-03-05: Created spec for role expansion with backward-compatible admin behavior.
- 2026-03-05: Added role utilities/backfill helper, user model role column, startup ensure role migration, admin role UI/routes updates, and manage_admin role output sync.

### Verification Evidence
- Command output summary: `python3 -m compileall -q app_db flask_app auth_server.py scripts models.py` completed successfully with exit code 0.
- Manual test summary: Code-level verification confirms role options are defined and normalized (`viewer`, `editor`, `approval1`, `approval2`, `admin`), startup backfill helper is wired (`ensure_user_role_column()`), admin create/edit routes persist role while preserving legacy `is_admin` fallback, admin template displays/edits roles, and `scripts/manage_admin.py` now sets/prints role with admin compatibility.
- Open follow-ups: Run interactive browser checks in admin panel against existing DB to confirm role edits and badges visually.

## SPEC-2026-03-05-route-permissions: Shared Role Decorators For Feature Authorization

### Metadata
- Owner: Codex
- Reviewers: N/A
- Status: Done
- Priority: P2
- Target date: 2026-03-05
- Related files: `flask_app/routes/permissions.py`, `flask_app/routes/docs.py`, `SPECS.md`

### Problem Statement
Role checks are currently embedded directly in feature route files. This is repetitive and makes it harder to apply consistent authorization patterns for future features like `editor`-only or `approval1`-only pages.

### Goals
- Add reusable decorators for role-based route authorization.
- Apply decorators to existing role-gated docs routes without changing current behavior.

### Non-Goals
- Full rewrite of every route in the app to use new decorators.
- Changes to existing role definitions or admin semantics.

### Constraints
- Keep `admin` backward-compatible as privileged bypass.
- Keep existing redirects/flash behavior compatible with current UX.

### Current State Notes
- Docs routes implement per-function manual checks using helper logic.
- The app already has normalized roles and `is_admin` compatibility.

### Proposed Design
#### API / Route changes
- Add `role_required(*roles, message=...)` decorator for login+role guard.
- Add `admin_required` decorator alias built on `role_required("admin")`.
- Refactor docs editor/upload/delete + housekeeping endpoints to use shared decorators.

### Implementation Plan
1. Add permissions decorator module under `flask_app/routes/`.
2. Refactor docs routes to use decorators and remove duplicated checks.
3. Verify compile and record evidence.

### Acceptance Criteria
- [x] Shared role decorator exists and supports one-or-many allowed roles.
- [x] Docs route protections still enforce current behavior:
- [x] `viewer` read-only
- [x] `editor`/`approval1`/`approval2`/`admin` can create/edit/delete docs
- [x] Housekeeping remains admin-only.
- [x] No compile/runtime import regressions.

### Verification Plan
- Run:
- `python3 -m compileall -q app_db flask_app auth_server.py scripts models.py`
- Code checks:
- Ensure protected docs endpoints use shared decorators.
- Ensure role matrix remains unchanged versus previous behavior.

### Risks and Mitigations
- Risk: decorator order/logic mismatch can alter auth behavior.
- Mitigation: keep `@login_required` semantics within decorator and preserve flash+redirect behavior.

### Rollback Plan
Revert `permissions.py` and docs route decorator refactor, restoring prior manual checks.

### Change Log
- 2026-03-05: Created spec for shared route permission decorators and docs integration.
- 2026-03-05: Implemented shared `role_required`/`admin_required` decorators and refactored docs route guards to use them.

### Verification Evidence
- Command output summary: `python3 -m compileall -q app_db flask_app auth_server.py scripts models.py` completed successfully with exit code 0.
- Manual test summary: Code-level verification confirms shared decorators exist in `flask_app/routes/permissions.py` and are applied to docs editor/delete/housekeeping endpoints with unchanged role matrix (`viewer` read-only, edit roles + admin write, housekeeping admin-only). `docs_upload_image` keeps JSON 403 behavior for unauthorized users.
- Open follow-ups: Optional browser verification for unauthorized redirect/flash behavior consistency on protected docs pages.

## SPEC-2026-03-05-role-only-auth: Remove Legacy `is_admin` Usage

### Metadata
- Owner: Codex
- Reviewers: N/A
- Status: In Progress
- Priority: P1
- Target date: 2026-03-05
- Related files: `app_db/models.py`, `app_db/user_roles.py`, `app_db/__init__.py`, `flask_app/routes/permissions.py`, `flask_app/routes/admin.py`, `flask_app/routes/docs.py`, `templates/base.html`, `templates/admin.html`, `templates/docs_index.html`, `scripts/manage_admin.py`

### Problem Statement
The codebase still uses legacy `is_admin` checks even though role-based authorization is now in place. The project is still in development and can use a fresh database, so role should be the single source of truth.

### Goals
- Remove `is_admin` from application-level auth logic and model usage.
- Use `role == "admin"` as the only admin authority check.
- Keep current feature behavior unchanged from a user perspective.

### Non-Goals
- Data migration from old `is_admin` values for existing DB snapshots.
- Full schema migration tooling beyond current startup ensure helper.

### Constraints
- Keep roles unchanged: `viewer`, `editor`, `approval1`, `approval2`, `admin`.
- Do not break existing docs/admin permissions behavior.

### Current State Notes
- `is_admin` is still referenced in templates, permission decorators, routes, and scripts.
- Role-based authorization already exists and can replace those checks.

### Proposed Design
#### API / Route changes
- Replace admin checks to use `normalize_role(current_user.role) == "admin"`.
- Remove route fallbacks that read form `is_admin`.

#### Data model / SQL changes
- Remove `is_admin` column from ORM `User` model class.
- Keep `ensure_user_role_column()` only for role column existence/backfill.

#### UI / Template changes
- Replace `current_user.is_admin` checks with role checks in navigation/docs/admin templates.

### Implementation Plan
1. Remove `is_admin` references from model and role helper APIs.
2. Update permissions/admin/docs routes to role-only checks.
3. Update templates and scripts to role-only logic.
4. Run compile verification and record evidence.

### Acceptance Criteria
- [x] No app code path depends on `User.is_admin`.
- [x] Admin-only access is enforced exclusively by role `admin`.
- [x] Docs permissions remain: viewer read-only; editor/approval1/approval2/admin can create/edit/delete.
- [x] Build verification command passes.

### Verification Plan
- Run:
- `python3 -m compileall -q app_db flask_app auth_server.py scripts models.py`
- Code checks:
- `rg is_admin` only returns historical/spec text, not active app logic/templates.

### Risks and Mitigations
- Risk: missed `is_admin` reference causes runtime error.
- Mitigation: global search + compile check after refactor.

### Rollback Plan
Restore prior role+`is_admin` compatibility code from git history.

### Change Log
- 2026-03-05: Created role-only auth spec and began removing `is_admin` usage.

### Verification Evidence
- Command output summary: Pending implementation.
- Manual test summary: Pending implementation.
- Open follow-ups: None.
