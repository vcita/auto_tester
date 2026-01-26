# Switch Setup Command and Config in Run/Heal Logs

## Overview

1. **Create-user function** — Implement a function that creates a new user (or onboard an existing new user): first login + dismiss **all one-time setup dialogs** until we **validate no dialog pops up on login** (so other tests don’t fail). This depends on a discovery step with Playwright MCP.
2. **CLI command `create_user`** — Creates a new user in vcita (signup + onboarding) and updates config.yaml so the system is ready to run tests with that account. No separate "switch setup" command.
3. **GUI: Switch setup** — "Switch setup" shows current setup, you edit and click "Create setup"; can later integrate "create user" flow if desired.
4. **Config in run logs** — Persist active target config in `run.json` and runs_index.
5. **Config in heal requests** — Add a Config section to heal request markdown.

---

## 0. Discovery: Create user and one-time dialogs (Playwright MCP)

**Do this first**, before implementing the create-user function.

- Use **Playwright MCP** to manually go through the full flow of creating a user (signup if applicable) and first login.
- **Signup entry**: The signup link is at the **bottom of the login page**; start from the login URL (= config `target.base_url` + `/login`), then navigate to signup from there.
- Document:
  - **Signup steps** (if creation is via UI): From login page bottom link; form fields, submit, any email verification assumption.
  - **First-login flow**: every **one-time setup / onboarding dialog** that appears (welcome, tour, preferences, etc.).
  - For each dialog: **how to detect it** (selector, text, or role), **how to dismiss it** (button text, "Skip", "Later", "X", etc.), and order if multiple appear.
  - **Validation**: after dismissing all, log out and log in again; confirm **no dialog appears** on the second login (so the account is “ready” for other tests).
- Capture selectors and exact copy where possible so the automation can reliably detect and dismiss dialogs.
- Output: a short **script or steps document** (e.g. in `tests/_functions/create_user/` or `docs/plans/`) that the implementer of the create_user function will follow.

---

## 1. Create-user function (tests/_functions)

- Add a new function under `tests/_functions/`, e.g. **create_user** (or **create_test_user**), with the usual structure: `steps.md`, `script.md`, `test.py`.
- **Responsibilities**:
  - If user creation is via UI: go to login page, use the **signup link at the bottom**, then run the signup flow (from discovery) with given email/password (or env; default password `vcita123`).
  - **Login** with the new credentials (reuse or call `fn_login`).
  - **Dismiss one-time dialogs**: in a loop, detect known onboarding dialogs from the discovery doc (e.g. by role, text, or selector), dismiss each (click Skip / Later / Close), until for a short period (e.g. 5–10 s) no dialog appears.
  - **Validate**: log out, log in again; assert that **no dialog** appears within a timeout (e.g. 10 s). If a dialog still appears, fail or retry dismissal so the account is only considered “ready” when second login is clean.
- The function should be callable with `(page, context, **params)` (e.g. `email`, `password`, optional `base_url`). Login URL is always **base_url + "/login"** (from config/context or params). The function does not write config; the **create_user** CLI command runs this function then updates config.
- **Default password** for new users (when not provided): `vcita123`.

---

## 2. CLI: create_user

### Usage

```text
python main.py create_user [--email EMAIL] [--password PASS] [--base-url URL]
```

- **--email** (optional): Account email. Default: `itzik+autotest.<timestamp>@vcita.com`.
- **--password** (optional): Password. Default: env `VCITA_TEST_PASSWORD` or **vcita123**.
- **--base-url** (optional): Base URL for signup/login. Default: from config (login URL = base_url + "/login").

### Behavior

1. Resolve email, password, base_url from args and config.
2. Launch browser (visible Chrome), run the create_user function (signup + first-login + dismiss onboarding dialogs).
3. On success, update `config.yaml` with the new account (target.auth.username, target.auth.password). base_url is updated only if --base-url was passed.
4. Print confirmation. The system is ready to run tests with the new user.

### Files

- **main.py**: `create_user` subparser and `cmd_create_user(args)` run the create_user flow then update config. No separate switch_setup command.

---

## 3. GUI: Switch setup

### UX

- In the GUI (e.g. top bar), add a **"Switch setup"** button.
- On click, open a **modal** (reuse existing modal pattern from [static/index.html](src/gui/static/index.html) and [static/app.js](src/gui/static/app.js)) that:
  - Shows **current setup**: base URL (login URL = base_url + "/login"), account email, password (masked, e.g. `••••••••`).
  - Provides **editable fields** for: base URL, email, password (optional; empty = keep current password).
  - Has a **"Create setup"** button that applies the form (same semantics as CLI: only send changed fields; backend merges with current config).

### API

- **GET /api/setup**  
  Returns current target config for the GUI (password masked), e.g.:
  ```json
  {
    "base_url": "https://app.vcita.com",
    "username": "user@example.com",
    "password_masked": true
  }
  ```
  (Login URL is base_url + "/login".)

- **POST /api/setup**  
  Body: `{ "base_url?", "username?", "password?" }`.  
  Merge with current config (omit or null = keep current). Write `config.yaml`. Return success and optionally the same shape as GET (password never returned).

Config path: same as main app (project root `config.yaml`); the GUI backend needs the project root (e.g. from `app.state` or existing convention).

### Files

- **Backend [src/gui/app.py](src/gui/app.py)**:
  - Implement `GET /api/setup` (load config, return target with password masked).
  - Implement `POST /api/setup` (read body, merge into config, write config.yaml).
  - Ensure app has access to project root (for `config.yaml` path).
- **Frontend [src/gui/static/index.html](src/gui/static/index.html)**:
  - Add "Switch setup" button in the top bar (e.g. next to Run Selected / Run All).
- **Frontend [src/gui/static/app.js](src/gui/static/app.js)**:
  - On "Switch setup" click: fetch GET /api/setup, open modal with current values in inputs, password field empty/masked.
  - On "Create setup" click: collect form (empty password = omit in request), POST /api/setup, close modal and show success; optionally refresh or show new setup summary.

---

## 4. Config in run logs

- **Runner** receives config (e.g. `config` or `target`) from main when constructing `TestRunner` / `StressTestRunner`; runner keeps a snapshot `run_config`.
- **RunStorage**:
  - `start_run(config=None)` stores `run_config` for the run.
  - `save_category_result` merges this config into the dict written to `run.json` (e.g. key `"config"`; password omitted or masked).
  - `finalize_run` adds the same config to the runs_index payload.
- **main.py**: Pass `config=load_config()` into runner constructors.
- **StressTestRunner**: Accept and pass config the same way so stress runs also record config.

---

## 5. Config in heal requests

- **HealRequestGenerator.generate(..., config=...)** — optional `config` argument.
- In `_build_content()`, if `config` is present, add a **"## Config"** section: base_url, login_url (derived: base_url + "/login"), username; do not include plaintext password.
- **Runner** passes `config=self.run_config` into `heal_generator.generate(...)`.

---

## 6. Implementation order

1. **Discovery (Playwright MCP)** — Manually create a user and go through first login; document every one-time dialog, how to dismiss it, and validate no dialog on second login. Produce script/steps for automation.
2. **Create-user function** — Implement `tests/_functions/create_user` from the discovery doc: signup (if UI), login, dismiss all onboarding dialogs in a loop, validate with a second login.
3. **Config in run logs and heal requests** — Runner/storage/heal only; no UI.
4. **CLI create_user** — Create a new user in vcita (signup + onboarding) and update config. Args: --email (optional), --password (optional), --base-url (optional).
5. **GUI Switch setup** — GET/POST /api/setup, modal with current setup and "Create setup" button.

---

## 7. Summary: How you provide base URL and account

| Context    | Base URL              | Account (email)     | Password                    |
|-----------|------------------------|---------------------|-----------------------------|
| **CLI create_user** | `--base-url` (optional; default from config) | `--email` (optional; default itzik+autotest.&lt;ts&gt;@vcita.com) | `--password` or env or vcita123 |
| **GUI**   | Editable field (prefilled from current; leave unchanged to keep) | Editable field       | Editable (empty = keep); stored masked in UI |

Both CLI and GUI update the same `config.yaml` and thus the same "current setup" used for the next run and stored in run/heal logs.

**Create-user flow**: Run `python main.py create_user` to create a new user and update config. **One run (create + tests):** `python main.py run --create-user` creates a new user then runs all categories; `python main.py run --create-user --category NAME` creates a new user then runs that category.
