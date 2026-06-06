# Changelog: Cancel and refund paid event

## 2026-06-06 — Initial migration (VCITA2-13856)
- Migrated event-payments.feature scenario 3 "Cancel and refund paid event".
- Isolated subcategory `cancel_refund` (point_of_sale denied).
- Reuses the record-payment helper; adds `cancel_event_with_refund` (event-page
  cancel with the refund option) and verifies the refunded payment via Payments
  Received search.
