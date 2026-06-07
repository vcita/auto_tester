# Script: Event payment request lifecycle

Playwright/Python notes for `test.py`.

## Navigation
- On new-dashboard (POV) accounts the event attendee menu no longer exposes the
  payment request, so it is reached through Billing & Invoicing → Orders.
  `open_attendee_payment_request` opens `/app/payments/orders`, scans `page.frames`
  for the order row matching the event service, clicks it, and waits for the Angular
  booking payment-status view (`span[data-qa='payment_status_state']`). The detail
  URL is cached and reused (a waived request drops out of the default Orders list).

## Reads / assertions (`event_payments_helpers.py`)
- `assert_event_payment_request` reads `div.summary-header h3` (service), `h2`
  (amount), `span[data-qa='payment_status_state']` (state, `:` stripped), and
  `[data-qa='display-name']` (client), and polls until all expected fields match.
- `edit_payment_request_amount` clicks `edit_payment_status`, fills
  `input[name="price"]`, and Saves.
- `cancel_payment_request` opens `ps-more-actions` → `waive_payment` → confirm
  `cancel_payment()`.

## Timing
- No fixed sleeps; bounded element/NAV waits capped at 5s, with the Orders-list
  reload loop (≤2 retries) absorbing order-indexing lag.
