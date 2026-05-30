# Changelog - Back-office Partial Refund

## 2026-05-29 - Initial migration
- Migrated from `automation-js/features/salsa/partial-refund.feature` scenario 1 (`@gate`).
- Own isolated account with `point_of_sale` denied before login (resolves the explore-first open decision: denial IS required to surface the legacy Record payment dialog; toggling mid-session fails due to cached flags).
- Quick Actions legacy custom-item dialog; refund + payment-page assertions via shared `partial_refund_helpers`.

## 2026-05-29 - Stabilization & validation
- Reworked `_fill_record_payment_dialog` for the modern Vue "Record payment" dialog: combobox -> Custom item, dynamic item-name field, Cash method, cross-frame helpers.
- Added `_open_and_select_client` retry loop to absorb client-indexing lag in the picker.
- Validation: focused run 41.8s PASS; stress_test 10/10 PASS (100%), stamped STABLE in `_category.yaml`.
