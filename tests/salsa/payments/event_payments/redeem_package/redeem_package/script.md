# Script: Redeem event payment request with package

Helpers in `event_payments_helpers.py`.

## Step 1 — Redeem with package
- `redeem_with_package(page, context)`: open the attendee payment request (Billing &
  Invoicing -> Orders -> event order), click `button[data-qa='redeem_package']`, and
  wait for the payment state to flip to PAID.

## Step 2 — Verify
- `assert_event_payment_request(...)`: re-open the request and assert
  **PAID / $0.00 / pack man / <event>** (reads `payment_status_state`,
  `div.summary-header h2` amount, `display-name`, `div.summary-header h3`).
