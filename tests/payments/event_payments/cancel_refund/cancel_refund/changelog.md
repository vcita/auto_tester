# Changelog: Cancel and refund paid event

## 2026-06-06 — Initial migration (VCITA2-13856)
- Migrated event-payments.feature scenario 3 "Cancel and refund paid event".
- Isolated subcategory `cancel_refund` (point_of_sale denied).
- Reuses the record-payment helper; adds `cancel_event_with_refund` (event-page
  cancel with the refund option) and verifies the refunded payment via Payments
  Received search.

## 2026-06-07 — Restore legacy refund-detail assertion + wait audit
- Scope fix: legacy `payment was refunded` opens the payment from Payments Received
  and asserts the detail header `Payment for <event>` (goToPayment +
  getPaymentNameText). The migration previously stopped at list-row presence; it
  now calls the new `open_payment_detail_and_assert_title`, which clicks into
  `/app/transactions/{uid}` and asserts `div.summary-header h3`.
- Wait audit (shared `event_payments_helpers.py`): element interactions stay at the
  5s cap (`UI_TIMEOUT`); navigation/frame-readiness budgets (`PAGE_TIMEOUT`,
  `NAV_TIMEOUT`) halved 20000→10000 as documented bounded exceptions (nested
  POV/Angular/Vue iframe boot legitimately exceeds 5s); `ORDERS_RELOAD_RETRIES` 3→2;
  removed the fixed `wait_for_timeout(2000)` after event cancel (now best-effort
  waits for the confirm control to detach). External client-portal navigation uses a
  documented 10s budget (`CP_NAV_TIMEOUT`).
