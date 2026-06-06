# Script: Event payment request lifecycle

Playwright/Python notes for `test.py`.

## Navigation
- The event page (`/app/events/{uid}`) renders in the Angular frontage iframe; the
  attendee list is a nested Vue iframe. `open_attendee_payment_request` finds the
  attendee activator in whichever frame holds it, clicks it, then clicks the
  "Go to payment status" menu item, and waits for the Angular payment-request view
  (`span[data-qa='payment_status_state']`).

## Reads / assertions (`event_payments_helpers.py`)
- `assert_event_payment_request` reads `div.summary-header h3` (service), `h2`
  (amount), `span[data-qa='payment_status_state']` (state, `:` stripped), and
  `span.contact-name` (client), and polls until all expected fields match.
- `edit_payment_request_amount` clicks `edit_payment_status`, fills
  `input[name="price"]`, and Saves.
- `cancel_payment_request` opens `ps-more-actions` → `waive_payment` → confirm
  `cancel_payment()`.

## Timing
- No fixed sleeps; bounded UI waits (5s) and NAV waits (20s) for iframe (re)render.
