# Changelog: Wizard - populated profession

## 2026-06-08 — Created (VCITA2-13903)
- Migrated legacy "user sees populated profession in preliminary step". New
  `payment_wizard_ui` opens the onboarding wizard from the checklist and reads the
  preliminary profession across the 3-level iframe; asserts it equals `Legal services`
  (prepopulated from `business_category=legal_services`).

## Wait audit (pre-PR)
- `WIZARD_LOAD_TIMEOUT=20s` (payment_wizard_ui): justified — wizard mounts through a 3-level
  iframe; element interactions capped at 5s.
- `CATEGORY_POLL_SECONDS=10s` (gateway_setups_api): justified — bounded read-back for the
  eventually-consistent `business_category` admin write (mirrors `wait_for_business_country`).
