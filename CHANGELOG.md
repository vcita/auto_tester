# Changelog

Global changes to the vcita Test Agent framework. Per-test changes are tracked in each test's own `changelog.md`.

---

## 2026-04-14 — Per-Category Account Creation at Runtime

**Branch:** `VCITA2-12938-Per-Category-Account-Creation-at-Runtime`

### Added
- **Per-category account creation** -- the runner now creates a fresh business account via the API before each category run and deletes it on success. No more shared accounts between categories.
- **`--env` flag** on `run` and `stress_test` commands -- target `production`, `integration`, or any feature-env by name.
- **`--no-auto-account` flag** -- opt out of per-category account creation and use the `config.yaml` account instead.
- **`cleanup_accounts` command** -- find and delete orphaned automation accounts with `--dry-run` and `--older-than` filters.
- **`src/runner/account_factory.py`** -- account creation, deletion, feature flag setup, and a local ledger (`.accounts/ledger.json`) to track created accounts.
- **`src/runner/env_config.py`** -- environment URL resolution for production, integration, and feature environments.
- **`.env` file support** -- `python-dotenv` loads a gitignored `.env` at startup for local token configuration.
- **`VCITA_ADMIN_TOKEN`** environment variable -- used for account deletion and feature flag setup.

### Changed
- **`run` command** defaults to auto-creating accounts on the `integration` environment (previously used a single hardcoded account from `config.yaml`).
- **`create_accounts.py`** simplified -- now delegates to `account_factory.py` instead of duplicating API logic.
- **`runner.py`** -- orchestrator manages account lifecycle (create before category, delete after success, keep on failure for debugging).
- **Login function** updated to accept credentials from the auto-created account context.
