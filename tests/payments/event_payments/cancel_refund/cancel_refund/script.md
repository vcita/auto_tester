# Script: Cancel and refund paid event

Helpers in `event_payments_helpers.py`.

## Step 1 — Pay full
- `pay_for_event(page, context, "10")`: record a full Cash payment via the
  legacy take-payment dialog (point_of_sale denied).

## Step 2 — Cancel event with refund
- `cancel_event_with_refund(page, context)`: open `/app/events/{uid}`, click the
  cancel control (`button[data-qa='cancel']`), tick the refund checkbox
  (`md-checkbox[ng-model="dialog.issue_refund"]`), confirm
  (`button[data-qa='confirm-cancel-event']`).

## Step 3 — Payment refunded
- `search_payments(page, context, "first", "Payment for <event>", 1)`: the
  refunded payment is listed in Payments Received.
