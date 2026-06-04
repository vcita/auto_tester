# Changelog: estimate_deposit_offline

## 2026-06-04 — Initial migration
- Migrated from `automation-js/features/salsa/deposits.feature` ("Business creates estimate
  with offline deposit, client approved it").
- Setup via API: create `product21` ($80), create estimate `bestimate_offline` + `$10` fixed deposit
  with `can_client_pay=false` (offline-only). No mock-gateway connect (an offline deposit is
  never paid online; the shared account already has the gateway from the prior CP scenario).
- Client-portal flow in `deposits_cp_ui.py`: open pending estimate, verify deposit DUE $10.00
  with only the "Approve" action (no online pay), approve via the confirm dialog, verify the
  offline-deposit page ($10.00), re-open from the approved tab, verify deposit OFFLINE.
- Estimate resolved dynamically by title (account shared across the subcategory; not `#0000001`).
- Legacy created the estimate via the BO UI; that path is covered by `estimate_deposit_bo`, so
  this scenario uses API setup and focuses on the distinct CP offline-approval behavior.
