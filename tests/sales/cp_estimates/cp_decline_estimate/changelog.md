# Changelog — Client Declines Estimate In CP

## 2026-06-09 — Initial build (VCITA2-14024)
- Migrated from automation-js `features/steps/cp/estimates.feature` scenario
  "Client declines estimate".
- Phases: steps.md → script.md → test.py.
- Reuses `tests/sales/estimates_helpers.py` (relocated from `tests/sales/estimates/`
  to the Sales category root so both the Estimates and CP-Estimates subcategories
  can import it). Added helpers: `create_estimate_api`, `cp_perform_estimate_action`,
  `assert_cp_estimate_status`.
- CP decline selectors verified live on integration: `button[data-qa="estimate-decline"]`
  → dialog `.dialog-containter` → `button.decline-button-text`; resulting status
  "Declined on <date>". Back-office state asserted as REJECTED.
- Estimate created via API with a free-form line item (no shared catalog dependency).
- Stabilization: 10-iteration stress surfaced 1 flake (30s default-timeout hang on the
  CP estimate-title click when a Vue overlay intercepted the pointer). Added a bounded
  `cp_click` helper (visibility wait + scroll + explicit-timeout click with a forced-click
  fallback) and routed all CP clicks through it so transient overlays can no longer stall
  on Playwright's 30s default.
