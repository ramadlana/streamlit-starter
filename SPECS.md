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

