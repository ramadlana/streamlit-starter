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
- Whitelist fonts to `inter`, `mirza`, and `roboto` in Quill config; use CSS to style reading surface default with Aref Ruqaa.
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
- [x] Editor uses Quill with simplified toolbar including font selector limited to Inter, Mirza, and Roboto.
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
- [x] Docs read page shows creator identity and created/updated timestamps at the bottom of content.

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
- 2026-03-05: Expanded docs read page to include footer metadata (created by, created at, updated at).
- 2026-03-05: Updated docs read page timestamps to render as human-readable values in browser-local timezone via client-side formatting.

### Verification Evidence
- Command output summary: `python3 -m compileall -q app_db flask_app auth_server.py scripts models.py` completed successfully with exit code 0.
- Manual test summary: Code-level verification completed for required route definitions, CSRF form token presence, Quill font whitelist config, image paste upload path (`uploads/attachments/docs`), URL image embedding workflow, updated Medium-like reader/editor template + CSS structure, search ranking logic (title/slug matches ranked above content-only matches), docs index card preview extraction (10-word short content from summary/content), attachment housekeeping logic (orphan detection + admin/CLI entrypoints), admin docs deletion flow wiring (modal), role-based docs permissions (`viewer` read-only; `editor`/`approval1`/`approval2`/`admin` can create/edit/delete), docs footer metadata rendering (creator + created/updated timestamps), and browser-local human-readable datetime formatting on docs view. Live browser/manual interaction was not executed in this run.
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
- Status: Done
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
- 2026-03-05: Completed role-only migration across model/routes/templates/scripts and removed active `is_admin` references.

### Verification Evidence
- Command output summary: `python3 -m compileall -q app_db flask_app auth_server.py scripts models.py` completed successfully with exit code 0.
- Manual test summary: Code-level verification confirms `is_admin` is no longer referenced in active app code (`app_db`, `flask_app`, `templates`, `scripts`), admin authorization is role-only (`admin`), and docs permissions remain unchanged functionally under role checks.
- Open follow-ups: Run UI sanity checks on admin panel and docs flows against a fresh DB schema.

## SPEC-2026-03-05-table-style-unification: Shared Compact Table Styling

### Metadata
- Owner: Codex
- Reviewers: N/A
- Status: Done
- Priority: P2
- Target date: 2026-03-05
- Related files: `templates/admin.html`, `static/css/form_and_table.css`, `SPECS.md`

### Problem Statement
Table styling is inconsistent across pages. The admin table uses separate inline styles, while CRUD pages already use a compact shared table style that is preferred.

### Goals
- Make admin table use shared table CSS patterns from CRUD pages.
- Keep table layout compact and responsive/snappy.

### Non-Goals
- Full redesign of modals or non-table page sections.
- Data or route logic changes.

### Constraints
- Prefer shared CSS classes over per-page inline table styles.
- Preserve existing admin actions and modal behavior.

### Implementation Plan
1. Wire admin page to include `form_and_table.css`.
2. Refactor admin table markup to use shared classes (`crud-panel`, `crud-table-wrapper`, `crud-table`).
3. Keep only minimal admin-specific styles for header and modals.
4. Verify compile and update evidence.

### Acceptance Criteria
- [x] Admin table uses shared compact table styling from `form_and_table.css`.
- [x] Table appears compact and consistent with `dummydata_crud` style.
- [x] No admin action regressions (edit/delete modals still work).

### Verification Plan
- Run:
- `python3 -m compileall -q app_db flask_app auth_server.py scripts models.py`
- Manual checks:
- Open `/admin` and confirm compact table spacing and scroll behavior.
- Confirm edit/delete modal triggers still function.

### Risks and Mitigations
- Risk: class-name overlap may affect non-admin sections.
- Mitigation: keep admin-specific overrides scoped to `.admin-container`.

### Rollback Plan
Revert `admin.html` table class refactor and restore previous inline table styles.

### Change Log
- 2026-03-05: Created spec for admin table style unification using shared CRUD CSS.
- 2026-03-05: Refactored admin table to shared `crud-panel`/`crud-table-wrapper`/`crud-table` classes and wired shared CSS include.

### Verification Evidence
- Command output summary: `python3 -m compileall -q app_db flask_app auth_server.py scripts models.py` completed successfully with exit code 0.
- Manual test summary: Code-level verification confirms admin table markup now uses shared compact table classes from `form_and_table.css`, and existing admin edit/delete modal JS hooks remain unchanged.
- Open follow-ups: Visual check on `/admin` for final spacing preference (column widths and row density) against production data volume.

## SPEC-2026-03-05-docs-sync: Rescan And Align Project Documentation

### Metadata
- Owner: Codex
- Reviewers: N/A
- Status: Done
- Priority: P2
- Target date: 2026-03-05
- Related files: `AGENTS.md`, `README.md`, `SPECS.md`

### Problem Statement
After recent feature and authorization changes, project documentation drifted from code reality in a few areas (stack versioning, docs routes, and editor font details), which increases onboarding and maintenance risk.

### Goals
- Re-scan implementation files and align key documentation files with current behavior.
- Keep updates limited to factual mismatches and avoid changing runtime behavior.

### Non-Goals
- Feature implementation changes.
- Adding new architecture patterns beyond what already exists in code.

### Constraints
- Preserve existing spec history sections.
- Keep updates concise and directly traceable to source code.

### Current State Notes
- `requirements.txt` pins Flask 3.1.2, while `AGENTS.md` still said Flask 2.x.
- `README.md` docs route list did not include upload/attachments/admin docs endpoints.
- Existing docs spec text referenced only Mirza/Roboto while editor currently whitelists Inter/Mirza/Roboto.

### Proposed Design
#### UI / Template changes
- None.

### Implementation Plan
1. Re-scan route/runtime/version sources.
2. Update `AGENTS.md` stack version statement.
3. Update `README.md` docs route inventory and docs timestamp behavior note.
4. Update spec text in `SPECS.md` to match current Quill font whitelist.

### Acceptance Criteria
- [x] `AGENTS.md` reflects Flask major version used by `requirements.txt`.
- [x] `README.md` route inventory includes current docs endpoints in `flask_app/routes/docs.py`.
- [x] `SPECS.md` docs-platform spec font details match `templates/docs_editor.html`.

### Verification Plan
- Run:
- `python3 -m compileall -q app_db flask_app auth_server.py scripts models.py`
- Code checks:
- Compare updated docs text against `requirements.txt`, `flask_app/routes/docs.py`, and `templates/docs_editor.html`.

### Risks and Mitigations
- Risk: Overwriting intentional historical details.
- Mitigation: only adjust objectively stale statements; keep historical spec sections intact.

### Rollback Plan
Revert documentation-only edits in `AGENTS.md`, `README.md`, and `SPECS.md`.

### Change Log
- 2026-03-05: Rescanned source files and aligned documentation with current implementation details.

### Verification Evidence
- Command output summary: `python3 -m compileall -q app_db flask_app auth_server.py scripts models.py` completed successfully with exit code 0.
- Manual test summary: Verified documentation updates against code in `requirements.txt`, `flask_app/routes/docs.py`, and `templates/docs_editor.html`; no runtime files changed.
- Open follow-ups: Optional pass to document Streamlit sample page inventory in more detail if needed for onboarding.

## SPEC-2026-03-05-docs-view-meta: Localized metadata footer for docs viewer

### Metadata
- Owner: Codex
- Reviewers: N/A
- Status: In Progress
- Priority: P2
- Target date: 2026-03-05
- Related files: `templates/docs_view.html`, `static/css/docs.css`

### Problem Statement
The documentation viewer currently places tags beside the summary and leaves the created/updated timestamps plus creator info in the footer, which disconnects them from the hero and presents raw server datetimes that ignore the reader’s timezone. Without a clear divider, the transition between the hero and the body content feels abrupt.

### Goals
- Render the creator along with the created and updated timestamps plus the tag chips directly below the title/summary (before the document body) so they’re top-of-page context.
- Keep timestamp text localized and human-friendly by using the user’s browser/OS timezone.
- Add a visible separator between this metadata strip and the main document content.
- Surface a delete control with confirmation inside the docs viewer so managers no longer need the card-level modal.

### Non-Goals
- Rework the docs index cards or any Streamlit views.
- Alter the underlying data model or introduce new metadata fields.

### Constraints
- Keep the change scoped to `templates/docs_view.html` and `static/css/docs.css` (plus any lightweight JS helper added under `static/`).
- Continue to rely on server-provided ISO timestamps for formatting, with the client doing the timezone conversion.
- No backend or database changes.

### Current State Notes
- Tags currently render near the summary inside `.docs-hero-tags`.
- Footer metadata mixes created/updated timestamps without relation to tags.
- Inline script is already formatting timestamps but uses a technical format and handles both created/updated nodes.

### Proposed Design
#### UI / Template changes
- Keep the hero header (title + summary) but add a metadata strip underneath that shows localized created/updated datetimes and the tag chips before any rich content appears.
- Continue using `<time class="js-local-datetime">` with `datetime`/`data-fallback`, letting the existing client formatter handle localization.
- Insert a subtle divider after the metadata strip and before `doc.content_html`.
- Add an inline delete form/button (with CSRF + confirmation) to the hero actions so admins can delete the document directly from this view.

#### Streamlit changes (if any)
- None.

### Implementation Plan
1. Update `templates/docs_view.html` to build a hero metadata strip (dates + tags) below the title/summary, add the separator, and ensure timestamps keep using the local formatter markup.
2. Adjust `static/css/docs.css` to style the metadata strip, inline tags, and the separator so the hero still feels cohesive.
3. Verify template renders correctly and that timestamps format in the browser before marking this spec done.

### Acceptance Criteria
- [ ] Created/Updated timestamps and tags sit in a metadata strip directly below the hero title/summary (above the separator) and display localized times.
- [ ] The timestamps use the user’s local browser/OS timezone and a readable format.
- [ ] There is a visible separator between the metadata strip and the document body content.
- [ ] A delete control with confirmation appears in the hero actions when `can_manage_docs` is `True`, matching the previous index behavior.

### Verification Plan
- Commands to run:
- `python3 -m compileall -q app_db flask_app auth_server.py scripts models.py`
- Manual checks to perform:
- Load a docs viewer in the browser, confirm the footer contains tags + localized updated time, and see the separator before the body.
- Negative tests (unauthorized/invalid input):
- Not applicable (template-only change).

### Risks and Mitigations
- There is a risk that moving tags to the footer will change layout expectations on smaller screens.
- Mitigation: Keep stacking order responsive and reuse existing tag styles so the change is primarily positional.

### Rollback Plan
Revert `templates/docs_view.html` and `static/css/docs.css` if the layout needs to go back to the original hero placement.

### Change Log
- 2026-03-05: Initial spec creation to capture the docs viewer metadata update request.

### Verification Evidence
- Command output summary: `python3 -m compileall -q app_db flask_app auth_server.py scripts models.py` completed successfully with exit code 0.
- Manual test summary: Not run (requires browser rendering); schedule a manual smoke check after deploying the docs viewer.
- Open follow-ups: Visual confirmation of the footer/tag placement and localized timestamps in the browser.

## SPEC-2026-03-05-docs-index-cards: Localized metadata and divider on docs list cards

### Metadata
- Owner: Codex
- Reviewers: N/A
- Status: In Progress
- Priority: P2
- Target date: 2026-03-05
- Related files: `templates/docs_index.html`, `static/css/docs.css`

### Problem Statement
Each documentation card on `/docs` currently surfaces the raw `updated_at` timestamp near the top, and tags sit directly below the summary, so readers must scan upward to find when a document last changed. Without a visual separation after the title, the card feels cluttered, and the delete button/modal—
which only works through an index-level modal—is mixing metadata with controls that should live in the document detail view.

### Goals
- Display the `updated_at` timestamp in a human-friendly way that respects the reader's local browser/OS timezone.
- Move the timestamp and tag chips to the bottom of the card so they serve as contextual metadata for the preview.
- Insert a separator between the title and the preview content so the hierarchy is clearer.
- Remove the delete button/modal from the card because deletion now occurs inside the docs viewer (see the viewer spec).

### Non-Goals
- Touch other pages (docs viewer, Streamlit) or change backend data.
- Display tools (e.g., delete) within the new metadata row.

### Constraints
- Keep the change limited to `templates/docs_index.html` and `static/css/docs.css`.
- Continue relying on server-provided ISO timestamps (`doc.updated_at.isoformat()`) for locale formatting on the client.
- No new backend data fields.

### Current State Notes
- Cards currently show `Updated {{ doc.updated_at }}` above the preview text.
- Tags render right after the preview and before the delete button.
- There is no divider between the title and the preview snippet.

### Proposed Design
#### API / Route changes
- None.

#### UI / Template changes
- Wrap the card title in a header block, insert a divider, and keep the preview text between the divider and footer.
- Add a footer row containing the localized updated timestamp and tag chips.
- Add a client-side script that formats every `.docs-card-updated .js-local-datetime` node via `Intl.DateTimeFormat`.
- Remove the index-level delete button/modal and its helper script since deletion now occurs on the docs viewer.

#### Streamlit changes (if any)
- None.

### Implementation Plan
1. Update `templates/docs_index.html` so each card has a divider, optional preview text, and a footer that contains localized `updated_at` plus tags.
2. Add the metadata formatter script to the bottom of `templates/docs_index.html` and remove the index-level delete modal logic.
3. Style the new divider/footer structure and ensure tags align right within `static/css/docs.css`.

### Acceptance Criteria
- [ ] Each docs card shows a separator between the title and the preview text (if present).
- [ ] The `updated_at` timestamp appears at the bottom of the card, is formatted through the browser's timezone, and is accompanied by the tag chips.
- [ ] Tags still behave as links and are styled consistently within the footer area.
- [ ] The cards no longer expose a delete button or modal; deletion occurs from the docs viewer.

### Verification Plan
- Commands to run:
- `python3 -m compileall -q app_db flask_app auth_server.py scripts models.py`
- Manual checks to perform:
- Open `/docs` in a browser and confirm the cards show the separator, the localized timestamp at the bottom, and the tags within the footer.

### Risks and Mitigations
- Risk: Footer layout might wrap awkwardly for cards without tags.
- Mitigation: Make footer flex-wrap and allow graceful stacking.

### Rollback Plan
Revert `templates/docs_index.html` and `static/css/docs.css` to their previous structure if needed.

### Change Log
- 2026-03-05: Added initial spec for docs index card metadata localization and divider.

### Verification Evidence
- Command output summary: `python3 -m compileall -q app_db flask_app auth_server.py scripts models.py` completed successfully with exit code 0.
- Manual test summary: Pending (requires browser rendering to confirm updated cards).
- Open follow-ups: Visual confirmation of the divider, localized timestamp, and bottom tags when viewing `/docs`.

## SPEC-2026-03-05-reusable-modal-system: Reusable Modal CSS/HTML Pattern

### Metadata
- Owner: Codex
- Reviewers: N/A
- Status: Done
- Priority: P2
- Target date: 2026-03-05
- Related files: `templates/admin.html`, `templates/base.html`, `templates/components/modal.html`, `static/css/base.css`, `templates/docs_view.html`

### Problem Statement
Modal markup and styling are currently embedded in `templates/admin.html`, so other pages cannot reuse the same look and behavior efficiently. This causes duplication and inconsistent modal UI patterns.

### Goals
- Promote the current `admin.html` delete modal look into a reusable modal design system.
- Provide reusable HTML and JS helpers so future pages can open/close consistent modals with minimal code.

### Non-Goals
- Migrating all confirmation prompts in every template to modals in this change.
- Changing backend routes or form handling behavior.

### Constraints
- Keep the existing visual baseline based on `templates/admin.html` delete modal style.
- Preserve current admin add/edit/delete modal functionality.
- Keep CSRF behavior unchanged for existing POST forms.

### Current State Notes
- `templates/admin.html` defines `.modal` and `.modal-content` inline with inline utility styles.
- Modal JS helpers (`showModal`, `closeModal`) and outside-click handling are local to `admin.html`.
- No shared modal component exists in `templates/components` or global CSS.

### Proposed Design
#### API / Route changes
- None.

#### Data model / SQL changes
- None.

#### UI / Template changes
- Add shared modal CSS primitives in `static/css/base.css`.
- Add reusable modal markup macro in `templates/components/modal.html`.
- Refactor `templates/admin.html` to use the shared macro/classes and remove inline modal CSS duplication.
- Add global modal JS helpers in `templates/base.html` (`window.AppModal.open/close/closeAll`) with consistent outside-click and Escape-to-close behavior.

#### Streamlit changes (if any)
- None.

### Implementation Plan
1. Add reusable modal CSS tokens/classes based on current admin delete modal styling.
2. Add Jinja macro component for modal wrapper structure.
3. Wire global modal helper script in base template.
4. Refactor admin modals to consume macro/classes and existing behavior.
5. Run compile verification and record evidence.

### Acceptance Criteria
- [x] Shared modal CSS exists in global stylesheet and is not duplicated inline in `admin.html`.
- [x] Reusable modal HTML macro/component exists and is used by admin modals.
- [x] Modal open/close behavior is reusable from global JS helpers and supports backdrop click + Escape key.
- [x] Admin add/edit/delete modal flows keep working with unchanged routes and CSRF fields.
- [x] Docs view delete action uses the shared modal instead of `confirm(...)`, preserving the same delete route and CSRF form.

### Verification Plan
- Run:
- `python3 -m compileall -q app_db flask_app auth_server.py scripts models.py`
- Manual/code checks:
- Confirm `templates/admin.html` uses shared modal macro/classes (no inline modal CSS block).
- Confirm admin modal buttons trigger global open/close helpers and backdrop/Escape close behavior.
- Confirm admin delete form action wiring and CSRF hidden input remain present.

### Risks and Mitigations
- Risk: Template macro usage could break existing modal content structure.
- Mitigation: Keep macro wrapper minimal and preserve inner form markup IDs/actions.
- Risk: Global JS might interfere with non-modal click handlers.
- Mitigation: Scope handlers to `.app-modal` elements and explicit API calls.

### Rollback Plan
Revert shared modal macro/CSS/JS additions and restore previous inline modal implementation in `admin.html`.

### Change Log
- 2026-03-05: Created reusable modal system spec based on admin delete modal baseline.
- 2026-03-05: Implemented shared modal CSS primitives, reusable template macro, and global modal open/close helpers; refactored admin add/edit/delete modals to use shared system.
- 2026-03-05: Scope update to apply shared modal system to docs view delete confirmation flow.
- 2026-03-05: Refactored docs view delete action to open shared modal confirmation using the reusable modal macro and global AppModal helpers.

### Verification Evidence
- Command output summary: `python3 -m compileall -q app_db flask_app auth_server.py scripts models.py` completed successfully with exit code 0.
- Manual test summary: Code-level verification completed for shared modal class usage, global helper wiring, admin modal trigger/actions, docs view delete modal wiring (route + CSRF preserved), and `confirm(...)` removal from docs view. Live browser interaction was not executed in this run.
- Open follow-ups: Optional browser smoke test to validate backdrop/Escape close interactions manually.

## SPEC-2026-03-05-docs-index-pagination: Efficient paginated docs list with adjustable page size

### Metadata
- Owner: Codex
- Reviewers: N/A
- Status: Done
- Priority: P1
- Target date: 2026-03-05
- Related files: `app_db/docs.py`, `flask_app/routes/docs.py`, `templates/docs_index.html`, `static/css/docs.css`

### Problem Statement
The docs index currently fetches up to 200 rows in one query and renders them all, which is less efficient as data grows and provides no page navigation or user control for list density.

### Goals
- Add server-side pagination for docs index and tag-filter pages.
- Allow users to adjust max rows per page via dropdown.
- Provide clear pagination UI (`< Previous`, page numbers with ellipsis, `Next >`) while preserving active filters/search.

### Non-Goals
- Changing docs schema or adding database indexes.
- Infinite-scroll behavior.

### Constraints
- Keep query efficient with SQL `LIMIT` and `OFFSET`.
- Preserve existing search/tag filtering behavior and route paths.

### Proposed Design
#### API / Route changes
- Keep existing routes (`/docs`, `/docs/tag/<tag>`) and add query params: `page` and `per_page`.

#### Data model / SQL changes
- Update `list_documents` to run:
  - a `COUNT(*)` query for total matches
  - a paginated data query with `LIMIT :limit_value OFFSET :offset_value`

#### UI / Template changes
- Add per-page dropdown in search row.
- Add pagination bar with previous/next controls, page chips, and ellipsis.
- Preserve `q`, `tag`, and `per_page` across page links.

### Acceptance Criteria
- [x] Docs listing queries are paginated in SQL (no fixed high-row fetch) and return total count + current page rows.
- [x] `/docs` and `/docs/tag/<tag>` accept and apply `page` + `per_page` query params safely.
- [x] `docs_index.html` provides adjustable per-page dropdown and pagination controls in the requested style.
- [x] Pagination links preserve active filters/search parameters.

### Verification Plan
- Run:
- `python3 -m compileall -q app_db flask_app auth_server.py scripts models.py`
- Manual/code checks:
- Confirm `list_documents` uses count + paginated query.
- Confirm docs index template renders previous/page/next controls and per-page selector.
- Confirm pagination links include preserved `q`, `per_page`, and `tag` context.

### Change Log
- 2026-03-05: Added server-side pagination and adjustable per-page controls for docs index/tag pages with updated UI.

### Verification Evidence
- Command output summary: `python3 -m compileall -q app_db flask_app auth_server.py scripts models.py` completed successfully with exit code 0.
- Manual test summary: Code-level verification completed for paginated SQL query pattern, route query param handling, and docs index pagination/dropdown rendering logic. Browser interaction not executed in this run.
- Open follow-ups: Optional browser smoke test for pagination UX and page-size switching behavior.

## SPEC-2026-03-05-docs-code-rendering: Preserve code formatting from editor to viewer

### Metadata
- Owner: Codex
- Reviewers: N/A
- Status: Done
- Priority: P1
- Target date: 2026-03-05
- Related files: `templates/docs_view.html`, `static/css/docs.css`

### Problem Statement
Code/Code Block formatting authored in the Quill editor was not visually represented on the docs viewer page, causing documentation snippets to appear as plain text.

### Goals
- Ensure docs viewer loads the required Quill presentation styles for rendered content.
- Add explicit readable code styles for inline code and blocks in docs prose.

### Acceptance Criteria
- [x] `docs_view.html` includes Quill Snow stylesheet so `.ql-*` markup from saved HTML is styled.
- [x] Inline code and code blocks are visually distinct in docs viewer.

### Verification Plan
- Run:
- `python3 -m compileall -q app_db flask_app auth_server.py scripts models.py`
- Manual/code checks:
- Confirm `docs_view.html` includes `quill.snow.css`.
- Confirm `docs.css` has dedicated `.docs-prose code` and `.docs-prose pre` styles.

### Change Log
- 2026-03-05: Added viewer-side Quill stylesheet and code block/inline code prose styles.
- 2026-03-05: Expanded scope to preserve pasted tab indentation when pasting plain text into Quill code blocks in docs editor.
- 2026-03-05: Added editor paste handler for code-block context and tab-size styling for code blocks.

### Verification Evidence
- Command output summary: `python3 -m compileall -q app_db flask_app auth_server.py scripts models.py` completed successfully with exit code 0.
- Manual test summary: Code-level verification completed for viewer CSS includes, prose code style rules, and editor code-block paste handler preserving plain-text indentation payload. Browser interaction not executed in this run.
- Open follow-ups: Browser smoke test to confirm pasted tab indentation is preserved in editor code blocks and reflected in `/docs/<slug>`.
