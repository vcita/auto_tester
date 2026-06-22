# Script: Pay for event via Point of Sale

Helpers in `event_payments_helpers.py`. The payment request is reached via
Billing & Invoicing -> Orders -> the eventattendance order row.

## Step 1 — Record via POS
- `record_event_payment_via_pos(page, context)`: open the payment request, click
  `take_payment` (opens POS with the event item pre-loaded), then POS checkout
  activator (`[data-qa="checkout-actions-activator"]`) -> Record payment
  (`[data-qa="checkout-action-record"]`) -> Cash (`md-select[name='payment_method']`)
  -> confirm (`[data-qa="take-payment-confirmation"]`).

## Step 2 — Orders PAID
- `assert_order_in_status(page, context, "PAID", "Sale #1 - <event>")`: filter
  Orders by status (`[name="status_filter"]` -> `[value="paid"]`) and assert the
  `f-ellipsis-tooltip.payment-title` row.

## Step 3 — Sale page
- `assert_sale_page(...)`: open the sale order and read `span.main-title` /
  `span.price` / `span.status-text` / `span.data-part` (frame-scanned); assert
  name, client, **PAID**, **$10.00**.

## Step 4 — Payments Received
- `search_payments(page, context, "first", "Payment for Sale #1 - <event>", 1)`.

## Step 5 — Conversation receipt
- `assert_cp_conversation_title(page, context, "Payment for <event>")`.
