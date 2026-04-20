# vcita Test Agent

AI-driven browser test automation framework for [vcita](https://www.vcita.com), built with Python and Playwright. Tests are black-box (no access to source code), self-healing, and organized as three-phase documents: `steps.md` (what) &rarr; `script.md` (how) &rarr; `test.py` (code).

**Key principles:**

- **Black-box testing** -- no access to vcita source code; tests discover UI like real users
- **Three-phase documents** -- every test has `steps.md`, `script.md`, and `test.py`
- **Self-healing** -- failed tests generate heal requests that guide automated fixes
- **Sequential execution** -- tests share browser state within a category
- **Real user actions only** -- no direct URL navigation (except login); simulate actual clicks

---

## Quick Start

**Prerequisites:** Python 3.10+, Google Chrome installed

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install Playwright browsers
playwright install chromium

# 3. Configure tokens
#    Create a .env file (gitignored) with API tokens for account creation/deletion:
#    VCITA_DIRECTORY_TOKEN=your_directory_token
#    VCITA_ADMIN_TOKEN=your_admin_token

# 4. Run tests (auto-creates a fresh account per category)
python main.py run --category clients
```

---

## CLI Commands

All commands are subcommands of `main.py`. Run `python main.py --help` for the full list.

### `run` -- Execute Tests

The primary command. Launches a Chromium browser, runs category setup, executes tests in `execution_order`, runs teardown, and reports results. On failure a heal request is auto-generated. Exit code is non-zero if any test fails.

**Flags:**

| Flag | Description |
|------|-------------|
| `--category, -c <name>` | Run a single category (e.g. `clients`) or subcategory path (e.g. `scheduling/appointments`). Omit to run all. |
| `--subcategory <name>` | Run only this subcategory within `--category`. Parent setup runs first, other tests are skipped. |
| `--selection, -s <path ...>` | Run multiple category/subcategory paths in one go. Mutually exclusive with `--category`. |
| `--headless` | Run the browser without a visible window (useful in CI). |
| `--keep-open` | Leave the browser open after the run (or after a failure) for manual inspection. |
| `--until-test "<Name>"` | Run the category up to (but not including) this test, dump context to `until_test_context.json`, and leave the browser open. Useful for starting a Playwright MCP debugging session from that point. Accepts a full path like `"Events/Schedule Event"` or just the test name. |
| `--debug-test "<Name>"` | Run the category up to and including this test, pausing (press Enter) after every action so you can observe what happens. Same name formats as `--until-test`. |
| `--env <name>` | Target environment for per-category account creation: `production`, `integration` (default), or a feature-env name (e.g. `aviv`). |
| `--no-auto-account` | Skip per-category account creation; use the account from `config.yaml` instead. |
| `--create-user` | Create a brand-new vcita user (signup + onboarding), update `config.yaml`, then run tests. Ensures a clean account. |
| `--create-user-email <email>` | Custom email for `--create-user` (default: `itzik+autotest.<timestamp>@vcita.com`). |
| `--create-user-password <pw>` | Custom password for `--create-user` (default: value from `config.yaml` or `vcita123`). |

**Examples:**

```bash
python main.py run                                             # Run all categories (auto-creates accounts per category)
python main.py run --category clients                          # Run only "clients"
python main.py run --category clients --env production         # Run on production
python main.py run --category scheduling/appointments          # Run only "appointments" under "scheduling"
python main.py run --category scheduling --subcategory events  # Run scheduling setup + events only
python main.py run --selection clients scheduling/events       # Run multiple paths together
python main.py run --headless --category payments              # Headless for CI
python main.py run --keep-open --category clients              # Leave browser open after run
python main.py run --no-auto-account --category clients        # Use config.yaml account instead of auto-creating
python main.py run --until-test "Edit Matter"                  # Stop before "Edit Matter", dump context
python main.py run --debug-test "Create Appointment"           # Step-by-step with pauses
python main.py run --create-user --category clients            # Fresh user then run
```

---

### `list` -- Discover Tests and Functions

Scans `tests/` and prints a tree of all categories, subcategories, and tests with their statuses. Can also list reusable functions from `tests/_functions/`.

**Flags:**

| Flag | Description |
|------|-------------|
| `--category, -c <name>` | Show only the specified category or subcategory. |
| `--functions, -f` | List reusable functions instead of tests. Shows name, parameters, and phase file status. |

```bash
python main.py list                        # Full test tree
python main.py list --category payments    # Only payments
python main.py list --functions            # Reusable functions (login, create_client, etc.)
```

---

### `status` -- Test Status Summary

Prints a table of test counts by status (Active, Pending, Disabled, Blocked) with percentages. Also shows how many tests are runnable (have `test.py`) vs. need exploration.

```bash
python main.py status
```

---

### `health` -- Generate Health Snapshot

Aggregates run results for a category and writes a `_health.json` file summarizing pass rates, recent failures, and trends. Currently supports the `payments` category only.

| Flag | Description |
|------|-------------|
| `--category, -c <name>` | Category to generate health for (default: `payments`). |

```bash
python main.py health
python main.py health --category payments
```

---

### `init` -- Scaffold a New Test

Creates a new test folder with template files (`steps.md`, `script.md`, `test.py`, `changelog.md`). Fill in `steps.md` with your test steps afterwards.

| Argument | Description |
|----------|-------------|
| `category` | Parent category (e.g. `clients`). |
| `test_name` | Test name in snake_case (e.g. `archive_matter`). Becomes the folder name. |

```bash
python main.py init clients archive_matter
python main.py init scheduling/services deactivate_service
```

---

### `gui` -- Launch Web GUI

Starts a FastAPI web server with a three-panel interface: test tree, test details/results, and artifacts (screenshots, videos, heal requests). Uses Server-Sent Events for real-time updates during test runs.

| Flag | Description |
|------|-------------|
| `--host <addr>` | Host to bind to (default: `127.0.0.1`). |
| `--port, -p <num>` | Port to listen on (default: `8080`). |

```bash
python main.py gui                              # http://127.0.0.1:8080
python main.py gui --host 0.0.0.0 --port 9090   # Accessible on LAN
```

---

### `create_user` -- Create vcita User

Opens a browser and runs the full vcita signup + onboarding flow (Welcome dialog, phone, address, business size), then updates `config.yaml` with the new credentials. Records a video of the flow. The system is ready to run tests against the fresh account afterwards.

| Flag | Description |
|------|-------------|
| `--email <email>` | Account email (default: `itzik+autotest.<timestamp>@vcita.com`). |
| `--password <pw>` | Password (default: from `config.yaml` or `vcita123`). |
| `--address <addr>` | Business address for the Welcome dialog (default: `123 Test Street`). |
| `--base-url <url>` | Override the base URL (default: from `config.yaml`). |

```bash
python main.py create_user
python main.py create_user --email me@example.com --password secret123
python main.py create_user --base-url https://staging.vcita.com
```

---

### `stress_test` -- Stress Test Categories

Runs one or more categories repeatedly for N iterations, then prints a summary report with pass/fail rates per category and per test.

| Flag | Description |
|------|-------------|
| `--categories, -c <name ...>` | One or more category names (required). |
| `--iterations, -i <num>` | Number of times to run each category (required). |
| `--headless` | Run without a visible browser. |
| `--keep-open` | Keep browser open on failure. |
| `--env <name>` | Target environment for per-category account creation (default: `integration`). |
| `--no-auto-account` | Skip per-category account creation; use the account from `config.yaml` instead. |

```bash
python main.py stress_test --categories clients --iterations 10
python main.py stress_test --categories clients scheduling payments --iterations 5 --headless
python main.py stress_test --categories clients --iterations 30 --env production --headless
```

---

### `cleanup_accounts` -- Delete Orphaned Accounts

Finds and deletes automation-created accounts that were not cleaned up (e.g. from failed runs). Uses the local account ledger (`.accounts/ledger.json`) to look up accounts via the admin API.

| Flag | Description |
|------|-------------|
| `--env <name>` | Target environment (default: `integration`). |
| `--dry-run` | List orphaned accounts without deleting them. |
| `--older-than <duration>` | Only target accounts older than this duration (e.g. `2h`, `30m`, `1d`). |

```bash
python main.py cleanup_accounts --dry-run                     # See what would be deleted
python main.py cleanup_accounts --env integration             # Delete all orphaned accounts
python main.py cleanup_accounts --older-than 2h               # Delete accounts older than 2 hours
```

#### Account Ledger

The runner maintains a lightweight local ledger at `.accounts/ledger.json` to track auto-created accounts. The file is a simple JSON array of email addresses:

```json
[
  "auto.api.clients.1713600000@test.com",
  "auto.api.scheduling.1713603600@test.com"
]
```

**How it works:**

- **On account creation** — the email is appended to the ledger (`record_created`).
- **On account deletion** — the email is removed from the ledger (`mark_deleted`). This happens automatically after a successful category run, or manually via `cleanup_accounts`.
- **On cleanup scan** — `list_auto_accounts` reads the ledger, verifies each email against the live admin API, and auto-removes entries where the API returns 404 (already deleted externally).

The ledger is **not** the source of truth — the live API is. The ledger is just an index so the runner knows which emails to look up (the admin API only supports exact-email queries, not prefix search).

**Inspecting the ledger directly:**

```bash
cat .accounts/ledger.json                # View all tracked emails
cat .accounts/ledger.json | python -m json.tool  # Pretty-printed
```

**The ledger is gitignored** and local to each developer's machine. If it gets out of sync (e.g. accounts deleted externally), `cleanup_accounts --dry-run` will reconcile it — stale entries are pruned automatically during the scan.

---

### `groom_heal_requests` -- Triage Heal Requests

Delegates to the Cursor AI via the `/groom_heal_requests` slash command. Reviews pending heal requests in `.cursor/heal_requests/` and marks them as open, fixed, reported, or expired.

```bash
python main.py groom_heal_requests
```

---

### `create_accounts.py` (standalone script)

Not a `main.py` subcommand. Creates business accounts per category via vcita's Create Business API. Requires a `VCITA_DIRECTORY_TOKEN` environment variable or `target.directory_token` in `config.yaml`.

| Flag | Description |
|------|-------------|
| `--env <name>` | Target environment: `production` (default), `integration`, or any custom feature-env name (e.g. `aviv`). |

```bash
python create_accounts.py
python create_accounts.py --env integration
VCITA_DIRECTORY_TOKEN=abc123 python create_accounts.py
```

---

## Cursor Slash Commands

The project includes 6 Cursor IDE slash commands (in `.cursor/commands/`) that automate common workflows:

| Command | Purpose |
|---------|---------|
| `/heal_test` | Fix a failing test -- reads the heal request, analyzes screenshot/video, debugs with Playwright MCP, and applies the fix. |
| `/implement_test` | Build a test end-to-end: from `steps.md` through `script.md` to `test.py`, using MCP to discover selectors. |
| `/debug_test` | Debug a specific test step-by-step using Playwright MCP to observe UI behavior. |
| `/stress_test` | Run stress tests on specified categories and report pass rates. |
| `/validate_tests` | Validate test files for correctness (missing files, broken references, etc.). |
| `/groom_heal_requests` | Review pending heal requests and mark them as open, fixed, reported, or expired. |

---

## Project Structure

```
auto_tester/
├── main.py                     # CLI entry point (all commands)
├── config.yaml                 # App, browser, target, and healing configuration
├── requirements.txt            # Python dependencies
├── create_accounts.py          # Standalone: create business accounts via API
├── debug_test_skeleton.py      # Template for standalone debug scripts
│
├── src/
│   ├── runner/                 # Test execution core
│   │   ├── runner.py           #   Orchestrator: browser lifecycle, setup/teardown, subcategories
│   │   ├── executor.py         #   Loads and runs individual test.py files
│   │   ├── account_factory.py  #   Per-category account creation/deletion via API
│   │   ├── env_config.py       #   Environment URL resolution (production, integration, feature-env)
│   │   ├── heal.py             #   Generates heal request markdown on failure
│   │   ├── context.py          #   Shared context dict management
│   │   ├── events.py           #   EventEmitter for real-time updates
│   │   ├── storage.py          #   Persists run results, screenshots, videos
│   │   ├── cli_reporter.py     #   Rich CLI output
│   │   ├── stress_test.py      #   Multi-iteration stress runner
│   │   └── models.py           #   TestResult, CategoryResult, RunResult
│   │
│   ├── discovery/              # Filesystem scanning
│   │   ├── test_discovery.py   #   Discovers categories via _category.yaml
│   │   └── function_discovery.py  # Discovers reusable functions
│   │
│   ├── models/                 # Data models
│   │   ├── category.py         #   Category, Test, SetupTeardown
│   │   ├── function.py         #   Function, FunctionParameter
│   │   └── enums.py            #   TestStatus, TestPriority
│   │
│   └── gui/                    # Web GUI
│       ├── app.py              #   FastAPI routes + SSE endpoint
│       └── static/             #   HTML, JS, CSS (dark theme, 3-panel layout)
│
├── tests/                      # All test categories and functions
│   ├── _functions/             #   Reusable functions (login, create_client, etc.)
│   ├── _params/                #   Shared test parameters (matter_entities.yaml)
│   ├── clients/                #   Client/matter management tests
│   ├── scheduling/             #   Scheduling tests (services, appointments, events)
│   └── payments/               #   Payment tests (settings, invoices, record_payments, refunds)
│
├── .accounts/                  # Account ledger (tracks auto-created accounts)
├── .context/                   # Persisted context files per category
├── .cursor/
│   ├── commands/               # Cursor slash commands
│   ├── rules/                  # AI rules (build phases, heal, project conventions)
│   ├── skills/                 # Agent skills (subcategory scaffolding, selector preferences)
│   ├── heal_requests/          # Auto-generated heal requests on failure
│   └── bug_reports/            # Product bug reports
└── snapshots/                  # Run artifacts
```

---

## Main Files Explained

| File | Purpose |
|------|---------|
| `main.py` | CLI entry point with all commands (`run`, `list`, `status`, `gui`, etc.) |
| `config.yaml` | Central configuration: target URL, credentials, browser settings, healing flags |
| `src/runner/runner.py` | **Orchestrator** -- starts a browser per category, creates a fresh account via API, builds execution plan from `execution_order`, runs setup &rarr; tests/subcategories &rarr; teardown, cleans up account on success, emits events, triggers heal on failure |
| `src/runner/executor.py` | **Test executor** -- dynamically imports `test.py`, finds `test_*` / `setup_*` / `teardown_*` / `fn_*` functions, calls them with `(page, context)`, captures screenshots on failure |
| `src/runner/account_factory.py` | **Account factory** -- creates and deletes business accounts via the vcita API; maintains a local ledger (`.accounts/ledger.json`) for cleanup |
| `src/runner/env_config.py` | **Env config** -- maps environment names (`production`, `integration`, feature-env) to API and app base URLs |
| `src/runner/heal.py` | **Heal request generator** -- on failure writes a markdown file to `.cursor/heal_requests/` containing error, screenshot path, context summary, and config |
| `src/runner/context.py` | **Context manager** -- shared `dict` that flows between tests in a category; persisted to `.context/` |
| `src/runner/events.py` | **Event system** -- `EventEmitter` with events like `TEST_STARTED`, `TEST_COMPLETED`, `TEST_FAILED`, `HEAL_REQUEST_CREATED`; consumed by CLI reporter and GUI SSE |
| `src/runner/storage.py` | **Run storage** -- saves runs to `tests/{category}/_runs/{run_id}/` with `run.json`, video, screenshots, and heal requests; maintains `runs_index/` |
| `src/runner/cli_reporter.py` | **CLI reporter** -- Rich-based console output subscribed to runner events |
| `src/runner/stress_test.py` | **Stress runner** -- runs categories N times and reports per-test pass rates |
| `src/discovery/test_discovery.py` | **Test discovery** -- scans `tests/` for `_category.yaml` files, identifies tests (folders with `steps.md`), builds execution order |
| `src/discovery/function_discovery.py` | **Function discovery** -- scans `tests/_functions/` and reads `_functions.yaml` for reusable function metadata |
| `src/gui/app.py` | **Web GUI** -- FastAPI app with REST endpoints, SSE for live updates, screenshot/video serving, and heal-request browsing |

---

## Test Three-Phase System

Every test goes through three phases, each producing a document:

```
steps.md  ──▶  script.md  ──▶  test.py
 (WHAT)         (HOW)          (CODE)
```

### Phase 1: `steps.md`

Human-readable description of **what** the test does. Written from the user's perspective with no implementation details.

```markdown
# Create Matter

## Objective
Verify that a new matter can be created from the dashboard.

## Prerequisites
- User is logged in (from _setup)

## Steps
1. Click "Quick Actions" button
2. Click "Add property"
3. Fill in First Name, Last Name, Email, Phone
4. Click Save

## Expected Result
- Matter appears in the matters list with the correct name

## Context Updates
- Save `created_matter_name` for subsequent tests
```

### Phase 2: `script.md`

Detailed **how** with verified Playwright code hints. Created by exploring the UI with Playwright MCP.

### Phase 3: `test.py`

Executable Python code. Every test function receives `(page, context)`:

```python
def test_create_matter(page, context):
    iframe = page.frame_locator('iframe[title="angularjs"]')
    iframe.get_by_role("button", name="Quick Actions").click()
    # ...
    context["created_matter_name"] = "John Doe"
```

### `changelog.md`

Each test also maintains a `changelog.md` that tracks every modification -- initial creation, heal fixes, selector updates, and flow changes. This prevents repeating failed approaches during healing.

---

## Building a New Category / Subcategory

The recommended way to add tests is to start with **Phase 1 only** (directory structure + `steps.md` files). Script and code files are created later using MCP exploration.

### 1. Gather Requirements

- **Parent category** -- e.g. `payments`, `scheduling`, `clients`
- **Subcategory name** -- snake_case plural noun, e.g. `invoices`, `refunds_credits`
- **Tests to include** -- list of test IDs with a one-line description each
- **Setup / teardown** -- whether the subcategory needs its own `_setup` and/or `_teardown`

### 2. Check Available Functions

Read `tests/_functions/_functions.yaml` to see what reusable functions exist (login, create_client, delete_service, etc.). Use `Call: function_name` in `steps.md` instead of duplicating logic.

```bash
python main.py list --functions
```

### 3. Create Directory Structure

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

### 4. Write `_category.yaml`

```yaml
name: Invoices
description: Tests for creating, editing, sending, and cancelling invoices

tests:
  - id: create_invoice
    name: Create Invoice
    status: pending
    priority: high
    description: Create a new invoice for a client
  - id: edit_invoice
    name: Edit Invoice
    status: pending
    priority: medium
    description: Edit an existing draft invoice
  # ...

status: active
priority: high
tags:
  - payments
  - invoices
```

**Rules:**
- `id` must exactly match the test folder name (snake_case)
- Test order in the `tests` list defines execution order
- Valid statuses: `active`, `pending`, `disabled`, `blocked`, `draft`
- Valid priorities: `critical`, `high`, `medium`, `low`

### 5. Write `steps.md` for Each Test

```markdown
# Create Invoice

## Objective
Verify that a new invoice can be created and sent to a client.

## Prerequisites
- User is logged in (from parent _setup)
- At least one client exists in the system

## Steps
1. Navigate to the Payments page
2. Click "Create Invoice"
3. Select a client from the dropdown
4. Add a line item with description and amount
5. Click "Save"

## Expected Result
- Invoice appears in the invoices list with status "Draft"
- Invoice total matches the line item amount

## Context Updates
- Save `created_invoice_id` for subsequent tests
```

### 6. Update Parent `_category.yaml`

If the parent category uses `execution_order`, add the new subcategory folder name:

```yaml
# payments/_category.yaml
execution_order:
  - settings
  - invoices          # <-- add here
  - record_payments
  - refunds_credits
```

### 7. Verify Discovery

```bash
python main.py list --category payments
```

### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Subcategory folder | snake_case, plural | `record_payments`, `invoices` |
| Test folder | snake_case, verb_noun | `create_invoice`, `record_payment_full` |
| Test ID in YAML | same as folder name | `create_invoice` |
| Display name | Title Case | `Create Invoice` |

### Common Mistakes to Avoid

- Do **not** create `script.md` or `test.py` at this phase -- those require MCP exploration (Phase 2 + 3)
- Do **not** include selectors, CSS classes, or code in `steps.md`
- Do **not** hardcode entity labels ("Properties" vs "Clients") -- keep steps entity-agnostic
- Do **not** skip verification steps for state-changing actions
- Do **not** duplicate function logic -- check `_functions.yaml` first and use `Call: function_name`

---

## The Heal Process

When a test fails, the framework automatically generates a **heal request** -- a markdown file containing everything needed to diagnose and fix the failure.

### How Heal Requests Are Generated

1. A test fails during execution in `runner.py`
2. `HealRequestGenerator` (in `src/runner/heal.py`) captures:
   - Error message and type
   - Screenshot of the failure state
   - Video recording of the full test run
   - Current `script.md` and `test.py` content
   - Shared context summary
   - Config (base URL, username -- no password)
3. A markdown file is written to `.cursor/heal_requests/heal_<test_id>_<timestamp>.md`

### Heal Workflow

```
Heal Request (failure context)
    │
    ▼
[1] Read changelog.md ── learn from past fix attempts
    │
    ▼
[2] Analyze screenshot + video ── see actual UI state at failure
    │
    ▼
[3] Debug step-by-step with Playwright MCP ── NEVER blind-fix
    │
    ▼
[4] Classify the issue
    ├── Selector changed ── element exists but locator is outdated
    ├── Flow changed ── UI flow is different (new steps, different order)
    └── Product bug ── the feature itself is broken
    │
    ▼
[5] Apply fix
    ├── Update script.md with verified Playwright code
    ├── Regenerate test.py
    ├── Update changelog.md
    └── Delete the heal request
```

### Key Heal Rules

- **Always read the changelog first** -- previous fix attempts are documented there; never repeat a failed approach
- **Always analyze the screenshot and video** -- the screenshot shows the end state, the video shows the journey
- **Always debug with Playwright MCP** -- execute test steps one by one in a real browser to find the exact failure point. Never guess from error messages alone
- **Use the same account** -- log in with the exact same credentials that ran the failing test
- **No retry loops** -- if a test fails due to timing, add or adjust the **wait** that proves readiness; do not add "retry click N times"
- **Event-based waits** -- use `element.wait_for(state="visible", timeout=30000)` instead of `page.wait_for_timeout(2000)`

### Issue Classification

| Error Pattern | Likely Cause | Action |
|---------------|--------------|--------|
| "Element not found" | Selector changed | Re-explore to find new selector |
| "Timeout waiting for" | Page structure changed | Re-explore the flow |
| "Expected X but got Y" | Logic/data issue | Check if product bug |
| "Navigation failed" | URL changed | Update URL in script |

### Escalation

After **5 failed MCP-based attempts** without resolution, create a standalone debug script:

1. Copy `debug_test_skeleton.py` to `debug_<category>_<test_name>.py`
2. Configure with the test's starting URL and context
3. Run directly: `python debug_<category>_<test_name>.py`

### Product Bugs

If the failure is caused by a product bug (not a test issue):

1. Create a bug report in `.cursor/bug_reports/`
2. Mark the test as `blocked` in `_category.yaml`
3. Delete the heal request

---

## Configuration Reference

All configuration lives in `config.yaml`:

```yaml
app:
  name: vcita Test Agent
  version: 1.0.0
  log_level: INFO                   # Logging verbosity

browser:
  type: chromium
  headless: false                   # Override with --headless flag
  slow_mo: 100                      # Milliseconds between actions
  timeout: 30000                    # Default timeout for Playwright operations
  viewport:
    width: 1280
    height: 720

execution:
  continuous: true                  # Keep running after failures
  parallel_tests: 1                 # Number of parallel tests (1 = sequential)
  retry_on_failure: 2               # Retry count for failed tests
  delay_between_runs: 60            # Seconds between runs in continuous mode
  screenshot_on_failure: true       # Capture screenshot on failure
  trace_on_failure: true            # Capture Playwright trace on failure

healing:
  enabled: true                     # Auto-generate heal requests on failure
  max_heal_attempts: 3              # Max heal retries before giving up
  re_explore_on_failure: true       # Re-explore UI when healing

tests:
  root_path: tests                  # Directory containing test categories
  category_file: _category.yaml     # Filename for category metadata

target:
  base_url: https://www.vcita.com   # Application base URL
  auth:
    username: user@example.com      # Test account email
    password: password123           # Test account password
```

---

## Web GUI

The project includes a browser-based interface for running and monitoring tests.

- **Left panel** -- test tree with categories, subcategories, and tests
- **Center panel** -- test details (steps/script/code) and execution results
- **Right panel** -- screenshots, videos, and heal requests from runs

**Tech stack:** FastAPI + vanilla HTML/JS/CSS + Server-Sent Events (dark theme)

```bash
python main.py gui
# Open http://127.0.0.1:8080
```

---

## Context System

Tests within a category share a `context` dictionary that flows through setup, tests, and teardown. This allows earlier tests to pass data to later ones (e.g. a created matter ID used by edit and delete tests).

```python
# In create_matter test:
context["created_matter_name"] = "John Doe"

# In edit_matter test:
matter_name = context["created_matter_name"]
```

Context is managed by `ContextManager` (`src/runner/context.py`) and persisted to `.context/` between runs. Each category has its own isolated context.

---

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `VCITA_DIRECTORY_TOKEN` | Directory token for creating business accounts (also: `target.directory_token` in `config.yaml`) |
| `VCITA_ADMIN_TOKEN` | Admin token for deleting accounts and setting feature flags (also: `target.admin_token` in `config.yaml`) |

A `.env` file in the project root is automatically loaded at startup (via `python-dotenv`). Add secrets there for local development -- it is gitignored and never committed.

---

## Automation Feature Flags

When a fresh account is auto-created (via `--env`), the runner applies a set of **automation feature flags** to suppress UI wizards, success modals, and empty states that interfere with test execution. These are defined in `src/runner/account_factory.py` under `AUTOMATION_FEATURE_FLAGS`:

| Flag | Purpose |
|------|---------|
| `hide_register_wizard` | Skip the post-registration onboarding wizard |
| `hide_payment_success_message` | Suppress the payment-success toast/modal |
| `hide_first_event_success_message` | Suppress the first-event-created success modal |
| `hide_empty_state` | Hide empty-state illustrations so list selectors work immediately |

Flags are sent as a single POST to `/admin/feature_flags/{user_id}/add_user_features` using the `VCITA_ADMIN_TOKEN`. This happens automatically after account creation — no per-test configuration is needed.

### Adding a new flag

1. Append the flag name to the `AUTOMATION_FEATURE_FLAGS` list in `src/runner/account_factory.py`.
2. Update the table above to document its purpose.

Only add flags here that should apply to **every** auto-created account. Product-specific flags that only certain tests need are not yet supported at the category or test level.

---

## Known Issues and Workarounds

| Issue | Workaround |
|-------|------------|
| **vcita service list refresh bug** -- after creating a service, the list doesn't refresh automatically | Navigate away (Settings page) and back to Services page |
| **Cloudflare blocking** -- Cloudflare sometimes blocks automated browser with "Just a moment..." page | Login function has retry logic with increased wait times; manual intervention sometimes needed |
| **Dropdown timing** -- dropdowns need time to populate options | Wait for the option to be visible before clicking: `option.wait_for(state="visible")` |
| **Matter list empty row** -- after creating a matter, sometimes shows as empty row | Navigation refresh workaround (same as services) |
