# Changelog: estimate_deposit_cp_sign

## 2026-06-04 — Initial migration
- Migrated from `automation-js/features/salsa/deposits.feature` ("Client signs, pays
  estimate's deposit and approve it").
- Setup via API (matches legacy): connect mock gateway (BO), create `product21` ($80),
  create signature-required estimate `bestimate_sign` + `$10` fixed deposit (`can_client_pay=true`).
- Client-portal flow in `deposits_cp_ui.py`: open pending estimate, verify deposit DUE $10.00,
  sign (canvas) + pay via mock gateway popup, verify success ($10.00), re-open from the
  approved tab, verify deposit PAID $10.00.
- Estimate resolved dynamically by title (account shared across the subcategory; not `#0000001`).
