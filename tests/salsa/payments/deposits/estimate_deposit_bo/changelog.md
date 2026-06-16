# Changelog — estimate_deposit_bo

## 2026-06-04 — Initial migration (VCITA2-13795)
- Migrated deposits.feature scenario 3 (back-office estimate deposit, approve & pay).
- Creates+sends an estimate with a $10 fixed deposit request, verifies SENT/DUE, approves
  and records the deposit as Cash, verifies APPROVED/PAID.
- Reuses estimates_helpers (open_new_estimate, set_title, add_custom_item, send_estimate,
  open_bo_estimate). Estimate uid resolved dynamically via the estimates API.
