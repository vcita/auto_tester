# Changelog — Client Approves Estimate In CP

## 2026-06-09 — Initial build (VCITA2-14024)
- Migrated from automation-js `features/steps/cp/estimates.feature` scenario
  "Client approves estimate".
- Phases: steps.md → script.md → test.py.
- Reuses `tests/sales/estimates_helpers.py` (`create_estimate_api`,
  `cp_perform_estimate_action`, `assert_cp_estimate_status`, `assert_cp_estimate`,
  `open_bo_estimate`, `assert_bo_estimate`).
- CP approve selectors verified live on integration: `button[data-qa="approve"]`
  → dialog `.dialog-containter` → `button.approve-button-text`; resulting status
  "Approved on <date>". Back-office state asserted as APPROVED.
- Estimate built via API with two free-form line items (service $100 +
  product_item200 $20, total 120).
