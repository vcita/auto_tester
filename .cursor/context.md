# Project Context & History

> This document preserves context and learnings from development sessions.
> It serves as a knowledge base when continuing work on a new computer or after long breaks.

## Project Overview

**vcita Test Runner** - An AI-driven browser test automation framework for vcita's web application. Built with Python, Playwright, and designed for self-healing tests.

### Key Principles
1. **Black-box testing** - No access to vcita source code; tests discover UI like real users
2. **Three-phase documents** - Every test has `steps.md` (what), `script.md` (how), `test.py` (code)
3. **Self-healing** - Tests can be automatically fixed when UI changes
4. **Sequential execution** - Tests share browser state within a category
5. **Real user actions only** - No direct URL navigation (except login), simulate actual clicks

---

## Architecture

### Core Components
- **Test Discovery** (`src/discovery/`) - Scans `tests/` folder, reads `_category.yaml` files
- **Test Runner** (`src/runner/`) - Executes tests sequentially, manages browser lifecycle
- **Event System** (`src/runner/events.py`) - Real-time updates via EventEmitter
- **Web GUI** (`src/gui/`) - FastAPI-based browser interface for running and monitoring tests

### Folder Structure
```
tests/
├── _functions/              # Reusable functions (login, logout, etc.)
├── clients/                 # Client/matter management tests
│   ├── _setup/             # Category setup (login + navigate)
│   ├── create_matter/      # Create new matter test
│   ├── edit_matter/        # Edit existing matter
│   ├── edit_contact/       # Edit contact info
│   ├── notes/              # Subcategory for notes tests
│   │   ├── add_note/
│   │   ├── edit_note/
│   │   └── delete_note/
│   └── delete_matter/      # Cleanup - runs last
└── scheduling/              # Scheduling tests
    ├── _setup/             # Navigate to Services page
    └── services/           # Subcategory for service management
        ├── create_service/
        ├── edit_service/
        └── delete_service/
```

### Context Flow
Tests pass data via a shared `context` dictionary:
- `created_matter_id` - Matter ID after creation
- `created_matter_name` - For verification
- `created_service_id`, `created_service_name`, `created_service_description`
- `created_note_content` - Note text for verification

---

## Key Technical Decisions

### 1. Playwright MCP for Debugging
The Playwright MCP browser tool is **critical** for:
- Identifying correct locators before writing tests
- Debugging failing tests step-by-step
- Verifying element states and timing

**Rule**: Never guess locators. Always verify with MCP first.

For tests that stay unfixed after several MCP attempts, use the standalone debug script: copy `debug_test_skeleton.py` to `debug_<category>_<test_name>.py` and follow the escalation steps in heal.mdc / heal_test.md.

### 2. Wait Strategy (CRITICAL)
**Never use `wait_for_timeout()` alone** for action completion. Always use conditional waits:

| Action Type | Wait Pattern |
|-------------|--------------|
| After click that opens dialog | `dialog.wait_for(state="visible")` |
| After click that navigates | `page.wait_for_url(pattern)` |
| After filling form + save | `confirmation_element.wait_for(state="visible")` |
| After element should hide | `element.wait_for(state="hidden")` |
| Small animation/focus delay | `wait_for_timeout(100-300)` (acceptable) |

### 3. Form Field Handling
- **`press_sequentially()`** - For most form fields (simulates user typing)
- **`fill()`** - Only for login fields (for reliability through Cloudflare)
- **`page.keyboard.type()`** - For rich text editors (`contenteditable`)
- **Autocomplete fields** - Click first, then type slowly with `press_sequentially()`

### 4. Iframe Handling
vcita uses iframes extensively. Pattern:
```python
angular_iframe = page.locator('iframe[title="angularjs"]')
angular_iframe.wait_for(state="visible")
iframe = page.frame_locator('iframe[title="angularjs"]')
# Then use iframe.get_by_role(...) etc.
```

### 5. Subcategory Execution Order
Use `run_after` in `_category.yaml` to control when subcategories run:
```yaml
# In notes/_category.yaml
run_after: edit_contact  # Runs after edit_contact completes
```

---

## Known Issues & Workarounds

### 1. vcita Service List Refresh Bug
**Issue**: After creating a service, the list doesn't refresh automatically.
**Workaround**: Navigate away (Settings page) and back to Services page.
**Status**: Bug reported to vcita.

### 2. Cloudflare Blocking
**Issue**: Cloudflare sometimes blocks automated browser with "Just a moment..." page.
**Handling**: The login function has retry logic with increased wait times.
**Manual intervention**: Sometimes needed during development/debugging.

### 3. Matter List Empty Row Display
**Issue**: After creating a matter, sometimes shows as empty row in list.
**Workaround**: Similar navigation refresh as services.

### 4. Dropdown Selection Timing
**Issue**: Dropdowns need time to populate options.
**Solution**: Wait for option to be visible before clicking:
```python
option = iframe.get_by_role("option", name=value)
option.wait_for(state="visible")
option.click()
```

---

## Development Workflow

### Adding New Tests
1. Create `steps.md` with human-readable test steps
2. Use Playwright MCP to explore the UI and identify locators
3. Create `script.md` with detailed actions and verified Playwright code
4. Create `test.py` by implementing the script
5. Run the category to verify it works
6. Update `_category.yaml` with test metadata

### Fixing Failed Tests
1. **Read the changelog** first - don't repeat failed approaches
2. **Analyze screenshot/video** from the failure
3. **Debug with MCP** - Execute steps one by one to find exact failure
4. Update `script.md` and `test.py` with fix
5. Log changes in `changelog.md`

### Running Tests
```bash
# CLI
python main.py run --category clients
python main.py run --category scheduling/services

# Web GUI
python main.py gui
# Open http://127.0.0.1:8080
```

---

## Web GUI

The web GUI provides:
- **Left panel**: Test tree with categories, subcategories, and tests
- **Center panel**: Test details (steps/script/code) and execution results
- **Right panel**: Screenshots, videos, and heal requests

**Tech Stack**: FastAPI + vanilla HTML/JS/CSS + Server-Sent Events

**Key Files**:
- `src/gui/app.py` - FastAPI routes and SSE endpoint
- `src/gui/static/index.html` - 3-panel layout
- `src/gui/static/app.js` - Frontend logic
- `src/gui/static/style.css` - Dark theme styling

---

## Test Status

### Completed & Working
- **clients** category (all tests pass):
  - `_setup` (login + navigate)
  - `create_matter`
  - `edit_matter`
  - `edit_contact`
  - `notes/add_note`
  - `notes/edit_note`
  - `notes/delete_note`
  - `delete_matter`

- **scheduling/services** subcategory:
  - `_setup` (navigate to Services)
  - `create_service` (with advanced edit)
  - `edit_service`
  - `delete_service`

### Planned (Not Yet Implemented)
- `scheduling/calendar` - Calendar management tests
- `scheduling/booking_settings` - Booking configuration
- `scheduling/online_booking` - Client booking flow
- `scheduling/reminders` - Reminder settings
- `booking` category - Existing tests need verification

---

## Credentials & Configuration

Test account and password come from **config.yaml** (target.auth; password not in git).

To **create a new user** and set it as the test account (signup + onboarding, then config updated):
```bash
python main.py create_user
```
Optional: `--email`, `--password`, `--base-url`. Default email: `itzik+autotest.<timestamp>@vcita.com`.

**One run (create user + run tests):** Create a new user then run all categories or a specific category:
```bash
python main.py run --create-user
python main.py run --create-user --category clients
```
Optional: `--create-user-email`, `--create-user-password`.

Login URL: **base_url + "/login"** (from config.yaml target.base_url)
App URL: **base_url + "/app/"**

---

## Rules Files Summary

| File | Purpose |
|------|---------|
| `project.mdc` | Architecture, principles, folder structure |
| `phase1_steps.mdc` | How to write `steps.md` files |
| `phase2_script.mdc` | How to write `script.md` files (includes wait strategy) |
| `phase3_code.mdc` | How to generate `test.py` files |
| `build.mdc` | Building new tests from steps |
| `heal.mdc` | Fixing failed tests (includes MCP debugging rules) |
| `module_planning.mdc` | Planning new test suites |

---

## Session History Highlights

### January 2026 Sessions
1. **Built clients category** - Full CRUD for matters with notes subcategory
2. **Established wait strategy** - Replaced all `wait_for_timeout` with element waits
3. **Fixed strict mode violations** - Made locators more specific
4. **Built scheduling/services** - Create, edit, delete services with advanced edit
5. **Created Web GUI** - FastAPI-based interface for test management
6. **Discovered vcita bugs** - Service list refresh, empty row display

### Key Learnings
- Always verify locators with MCP before writing tests
- Form fields that transform (like autocomplete) need special handling
- Sequential tests must verify start state, not navigate to it
- SSE connections need careful error handling for stability
- vcita has UI refresh bugs that require navigation workarounds

---

*Last Updated: January 22, 2026*
