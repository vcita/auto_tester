# Changelog: Wizard - profession required

## 2026-06-08 — Created (VCITA2-13903)
- Migrated legacy "user with no profession need to fill profession in preliminary step".
  Opens the wizard, asserts the currency-step next button is disabled, fills the profession
  autocomplete, and asserts the MCC clarification dialog appears.

## Wait audit (pre-PR)
- `WIZARD_LOAD_TIMEOUT=20s` (payment_wizard_ui): justified — wizard mounts through a 3-level
  iframe; element interactions capped at 5s.
