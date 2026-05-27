---
name: generate-subcategory
description: Scaffold a new test subcategory with _category.yaml and steps.md files for each test. Use when creating a new subcategory, adding a test group under an existing category, or when the user says "new subcategory", "add tests for", or "scaffold tests".
---

# Generate Subcategory

Create a new test subcategory folder with all Phase 1 files. This produces the directory structure, `_category.yaml`, and a `steps.md` per test. Script and code files are NOT created here (Phase 2+3 require MCP exploration).

## Prerequisites

Before running, gather from the user:

1. **Parent category** — e.g. `payments`, `scheduling`, `clients`
2. **Subcategory name** — snake_case plural noun, e.g. `refunds`, `invoices`
3. **Tests to include** — list of test IDs with a one-line description each
4. **Whether `_setup` / `_teardown` are needed** for this subcategory

Check `tests/_functions/_functions.yaml` for reusable functions before writing steps. Use `Call: function_name` instead of duplicating login, client creation, etc.

## Directory Structure to Create

```
tests/<parent>/<subcategory>/
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

## File Templates

### _category.yaml

```yaml
# <Subcategory Display Name>
# <One-line purpose>

name: <Display Name>
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

1. **Read** `tests/_functions/_functions.yaml` to know available functions
2. **Read** the parent category's `_category.yaml` to check for `execution_order` (you may need to add the new subcategory there)
3. **Create** the subcategory folder and all subfolders
4. **Write** `_category.yaml` with all test entries
5. **Write** `steps.md` for each test (and `_setup`/`_teardown` if needed)
6. **Update** the parent category's `_category.yaml` if it uses `execution_order` — add the new subcategory folder name
7. **Verify** with `python main.py list --category <parent>` to confirm discovery works

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Subcategory folder | snake_case, plural | `record_payments`, `invoices` |
| Test folder | snake_case, verb_noun | `create_invoice`, `record_payment_full` |
| Test ID in YAML | same as folder name | `create_invoice` |
| Display name | Title Case | `Create Invoice` |

## Common Mistakes to Avoid

- Do NOT create `script.md` or `test.py` — those require MCP exploration (Phase 2+3)
- Do NOT include implementation details (selectors, waits, code) in steps.md
- Do NOT hardcode entity labels ("Properties" vs "Clients") — keep steps entity-agnostic
- Do NOT skip the verification step for state-changing actions
- Do NOT duplicate function logic — check `_functions.yaml` first
