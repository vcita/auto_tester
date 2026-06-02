# Changelog

- Migrated legacy `Calendar - display multiple staff`.
- Preserved `@unstable` scope, staff filtering, all-staff visibility, and switched-staff visibility intent.

## 2026-06-02 - Generate directory token at runtime (VCITA2-13777)

**Phase**: Shared API helper (`tests/scheduling/calendar/calendar_api.py`)
**Author**: Cursor AI
**Reason**: The final `switch_logged_in_staff` step did partner SSO via `partner_headers()`, which required a pre-provisioned `VCITA_DIRECTORY_TOKEN` env var. It was missing in the run environment, raising `ValueError` and failing the test (and cascade-skipping Print Calendar).

**Changes**:

- `partner_headers(context)` now resolves the directory token via `resolve_directory_token(context)` instead of requiring `VCITA_DIRECTORY_TOKEN`.
- `resolve_directory_token` mirrors legacy automation-js (`api/directories.js`): prefer the `VCITA_DIRECTORY_TOKEN` override, else reuse/generate one at runtime from the admin token + `directory_id` via `GET`/`POST /platform/v1/tokens` (admin auth). Both inputs are already available (admin token from `.env`, `directory_id` from the runner context).
- Reuses the shared `admin_headers()` from `tests/account_api.py`.

**Test run**: `scheduling/calendar` (agenda_view -> display_multiple_staff) — **Display Multiple Staff PASSED (29.7s)**, completing the partner-SSO staff switch without the env secret.
