# Script: Paying for an invoiced event

Helpers in `event_payments_helpers.py`.

## Step 1 — Invoice the event
- `invoice_event(page, context, "event_invoice", "blablablabla")`: open the event
  payment request, click `send_an_invoice`, fill the wizard title
  (`[data-qa="itemizable-details-header"] input`) and the From billing address
  (`itemizable-from-fold` -> edit -> textarea), then send
  (`[data-qa='itemizable-dialog-main']`). The event line item is pre-included.

## Step 2 — Pay the invoice
- `pay_for_invoice(page, context, "event_invoice #0000001", "10")`: open the invoice
  order from Orders and record a Cash payment (same take-payment dialog as events).

## Step 3 — Invoice page
- `assert_invoice_page(...)`: read `div.summary-header h3` (invoice_name),
  `div.invoice-item-content span` (service item), `[data-qa='display-name']` (client),
  `div.summary-header h2 span` (amount), `[data-qa='payment_status_state']` (state);
  assert **PAID / $10.00 / first last / <event> / event_invoice #0000001**.

## Step 4 — Payments Received
- `search_payments(page, context, "first", "Payment for event_invoice #0000001", 1)`.
