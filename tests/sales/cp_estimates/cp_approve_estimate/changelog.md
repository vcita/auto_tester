# Changelog — Client Approves Estimate In CP

## 2026-06-09 — Initial build (VCITA2-14024)
- Migrated from automation-js `features/steps/cp/estimates.feature` scenario
  "Client approves estimate".
- Phases: steps.md → script.md → test.py.
- Reuses `tests/sales/estimates/estimates_helpers.py` via the qualified import
  `from tests.sales.estimates import estimates_helpers` (`create_estimate_api`,
  `cp_perform_estimate_action`, `assert_cp_estimate_status`, `assert_cp_estimate`,
  `open_bo_estimate`, `assert_bo_estimate`).
- CP approve selectors verified live on integration: `button[data-qa="approve"]`
  → dialog `.dialog-containter` → `button.approve-button-text`; resulting status
  "Approved on <date>". Back-office state asserted as APPROVED.
- Estimate built via API with two free-form line items (service $100 +
  product_item200 $20, total 120).

## 2026-06-11 — Review fixes (VCITA2-14024)
- Reverted the shared-helper relocation: `estimates_helpers.py` stays at
  `tests/sales/estimates/` (the rename had broken ~12 payments/sales modules that
  import it via `tests.sales.estimates.estimates_helpers`). CP tests now use that
  qualified import.
- Replaced the blind 2.5s sleep in `open_bo_estimate` with a bounded
  readiness poll (detail price rendered, capped at NAV_TIMEOUT).
