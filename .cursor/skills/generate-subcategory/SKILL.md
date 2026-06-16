---
name: generate-subcategory
description: Scaffold a new test subcategory with _category.yaml and steps.md files for each test. Use when creating a new subcategory, adding a test group under an existing category, or when the user says "new subcategory", "add tests for", or "scaffold tests".
---

# Generate Subcategory

Create a new test subcategory folder with all Phase 1 files. This produces the directory structure, `_category.yaml`, and a `steps.md` per test. Script and code files are NOT created here (Phase 2+3 require MCP exploration).

## Prerequisites

Before running, gather from the user:

1. **Owning team** — one of `backstage`, `maestro`, `salsa`, `spotlights`, `tango`, `tempo`. Determine it by looking up the test's product component on the company **Confluence "Squads responsibilities"** page (the source of truth; pageId `2615410911`) — read it live and map component → squad. See [`../team-taxonomy.md`](../team-taxonomy.md) for how to read the page and the selection order (Confluence > existing sibling > provenance hint > ask). Never scaffold a subcategory outside a team folder, and never assign a team from the legacy folder/provenance alone when the Confluence page says otherwise.
2. **Parent category (domain)** — e.g. `payments`, `scheduling`, `clients`. This is the account boundary, nested under the team: `tests/<team>/<domain>/`.
3. **Subcategory name** — snake_case plural noun, e.g. `refunds`, `invoices`
4. **Tests to include** — list of test IDs with a one-line description each
5. **Whether `_setup` / `_teardown` are needed** for this subcategory

Check `tests/_functions/_functions.yaml` for reusable functions before writing steps. Use `Call: function_name` instead of duplicating login, client creation, etc.

## Directory Structure to Create

```
tests/<team>/<parent>/<subcategory>/
├── _category.yaml
├── _setup/                    # only if needed
│   └── steps.md
├── _teardown/                 # only if needed
│   └── steps.md
├── <test_id_1>/
│   └── steps.md
├── <test_id_2>/
│   └── steps.md
└── ...
```

`<team>` is one of the canonical teams (a non-account "team group"); `<parent>` is the domain (account boundary). If the team or domain folder does not exist yet, create it — and ensure the team root has a group `_category.yaml` (`team: <team>`, `team_group: true`) per [`../team-taxonomy.md`](../team-taxonomy.md).

## File Templates

### _category.yaml

```yaml
# <Subcategory Display Name>
# <One-line purpose>

name: <Display Name>
team: <team>
description: <What this subcategory tests>

tests:
  - id: <test_folder_name>
    name: <Display Name>
    status: pending
    priority: <high|medium|low>
    description: <One-line description>
  # repeat for each test...

status: active
priority: <high|medium|low>
tags:
  - <parent_category>
  - <subcategory>
owner: QA Team
created_at: <YYYY-MM-DD>
```

**Rules:**
- `team:` must be one of the canonical teams and match the team folder the subcategory lives under
- `id` must exactly match the test folder name (snake_case)
- Test order in `tests:` list defines execution order
- Valid statuses: `active`, `pending`, `disabled`, `blocked`, `draft`
- Valid priorities: `critical`, `high`, `medium`, `low`

### steps.md (per test)

```markdown
# <Test Name>

## Objective
<One sentence: what this test verifies from the user's perspective>

## Prerequisites
- <What must be true before this test runs>
- <Reference context variables from prior tests if needed>

## Steps
1. <High-level user action — WHAT, not HOW>
2. <Next action>
3. ...

## Expected Result
- <Observable outcome that proves success>
- <Must verify actual data, NOT toast messages>

## Context Updates
- Save `<variable_name>` for subsequent tests
```

**Critical steps.md rules:**
- Describe WHAT to do, never HOW (no selectors, no code, no CSS)
- Each step is one user action, written from user perspective
- State-changing actions (create/update/delete) MUST have a verification step
- Verify by checking actual data (list items, page content, URL), never toasts
- Use `Call: function_name` for reusable operations (login, create_client, etc.)
- Do not define a UI-scoped action and later satisfy it with an API call. If the step says the user deletes, edits, creates, or navigates in the UI, that UI path is part of the test scope.
- Use API setup/cleanup only for prerequisites outside the behavior being tested, not as a replacement for a declared UI action.
- Keep steps concise — typically 5-10 steps per test
- Prerequisites reference context from `_setup` or prior tests in the subcategory

### steps.md for _setup (if needed)

```markdown
# <Subcategory> Setup

## Objective
Prepare the environment for <subcategory> tests.

## Prerequisites
- User is logged in (from parent category _setup)

## Steps
1. <Setup action>
2. ...

## Expected Result
- <What state the system should be in after setup>

## Context Updates
- Save `<variable>` for use by tests in this subcategory
```

### steps.md for _teardown (if needed)

```markdown
# <Subcategory> Teardown

## Objective
Clean up resources created during <subcategory> tests.

## Prerequisites
- Tests in this subcategory have run

## Steps
1. <Cleanup action — use Call: delete_client, Call: delete_service, etc.>

## Expected Result
- <All test data is cleaned up>

## Context Updates
- Clear `<variable>` from context
```

## Workflow

1. **Determine the team** per [`../team-taxonomy.md`](../team-taxonomy.md) and confirm the target path is `tests/<team>/<parent>/<subcategory>/`
2. **Read** `tests/_functions/_functions.yaml` to know available functions
3. **Read** the parent domain's `_category.yaml` (`tests/<team>/<parent>/_category.yaml`) to check for `execution_order` (you may need to add the new subcategory there). If the team/domain does not exist yet, create the team-root group `_category.yaml` (`team:` + `team_group: true`) and the domain `_category.yaml` (`team:` + `execution_order`).
4. **Create** the subcategory folder and all subfolders under the team
5. **Write** `_category.yaml` with `team:` and all test entries
6. **Write** `steps.md` for each test (and `_setup`/`_teardown` if needed)
7. **Update** the parent domain's `_category.yaml` if it uses `execution_order` — add the new subcategory folder name
8. **Verify** with `python main.py list --team <team>` (and `--category <team>/<parent>`) to confirm discovery places it under the right team

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Team folder | canonical team, lowercase | `tempo`, `salsa`, `spotlights` |
| Domain folder | snake_case, under a team | `tempo/scheduling`, `salsa/payments` |
| Subcategory folder | snake_case, plural | `record_payments`, `invoices` |
| Test folder | snake_case, verb_noun | `create_invoice`, `record_payment_full` |
| Test ID in YAML | same as folder name | `create_invoice` |
| Display name | Title Case | `Create Invoice` |

## Scope & Quality Guardrail (Design-Time)

Scaffolding sets the scope ceiling for the eventual test — if a behavior is missing from `steps.md`, it will be missing from `test.py`. Before finishing the scaffold, verify scope and quality are fully captured:

- Capture every behavior the subcategory is meant to cover. If you are scaffolding from an existing source (a spec, a legacy test, or a feature), do not drop any action, assertion, edge case, or data expectation.
- Every state-changing action (create/update/delete/move) MUST have a verification step that checks real data/state, never a toast.
- Declare in-scope UI actions as UI steps; only push prerequisites outside the tested behavior to API setup/cleanup.
- Keep steps entity-agnostic unless the scenario specifically asserts a displayed label.
- The runtime scope & quality check (docs agree with code, no weakened selectors/assertions) is performed when the test is built (`implement_test` / **build.mdc**) and when it is healed (`heal_test`); this design-time guardrail makes sure the scope exists to verify.

## Wait & Duration Awareness (Design-Time)

Design each subcategory so the eventual test runs fast, without giving up coverage:

- Prefer `Call:` reusable functions and API setup for prerequisites outside the tested behavior, so the test spends time only on the behavior it verifies.
- Keep steps minimal and avoid redundant navigation, but never drop a verification step or an in-scope UI action to shorten the flow.
- Leave timing/wait details to Phase 2 (`script.md`); do not encode fixed sleeps or implementation waits in `steps.md`.
- The full **Wait & Duration Audit** (no wasted retries, no fixed sleeps for action completion, no timeouts above the 5s cap, no avoidable duration) is mandatory at build time (**build.mdc** / `implement_test`) and heal time (`heal_test`); design steps so that audit can pass without dropping coverage.

## Common Mistakes to Avoid

- Do NOT scaffold a domain/subcategory directly under `tests/` — it MUST live under a team folder (`tests/<team>/<domain>/...`) with a `team:` field
- Do NOT create `script.md` or `test.py` — those require MCP exploration (Phase 2+3)
- Do NOT include implementation details (selectors, waits, code) in steps.md
- Do NOT hardcode entity labels ("Properties" vs "Clients") — keep steps entity-agnostic
- Do NOT skip the verification step for state-changing actions
- Do NOT duplicate function logic — check `_functions.yaml` first
