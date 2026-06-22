# Changelog: Pay for event

## 2026-06-06 — Initial migration (VCITA2-13856)
- Migrated event-payments.feature scenario 2 "paying for event" (partial then full).
- Isolated subcategory `pay_for_event` with `point_of_sale` denied so `take_payment`
  uses the legacy record-payment dialog.
- Reuses the event-payment-request navigation (Billing -> Orders -> order row) and
  adds frame-scan helpers for the record-payment dialog, Payments Received search,
  and the client-portal receipt conversation.
