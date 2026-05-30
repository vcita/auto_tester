# Changelog - POS Partial Refund

## 2026-05-29 - Initial migration
- Migrated from `automation-js/features/salsa/partial-refund.feature` scenario 2 (POS).
- Own isolated account (Point of Sale enabled) to match the legacy per-scenario account isolation.
- POS checkout custom-item record flow; refund + payment-page assertions via shared `partial_refund_helpers`.
- Refund dialog hosted in a nested frame; helper resolves the frame and waits for the confirm button to enable.

## 2026-05-29 - Stabilization & validation
- After recording the POS payment the page already shows the payment detail; removed redundant list navigation so the refund acts on the open payment.
- Hardened `_refund_amount_input`/`_refund_submit_button` to search all frames and wait for enablement (Vue dialog timing).
- Validation: focused run 26.9s PASS; stress_test 10/10 PASS (100%), stamped STABLE in `_category.yaml`.
