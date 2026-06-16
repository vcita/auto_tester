# Script: Pay for event (partial then full)

Playwright-oriented HOW for `test.py`. The payment request is reached via
Billing & Invoicing -> Orders -> the eventattendance order row (see
`event_payments_helpers.open_attendee_payment_request`).

## Step 1 — Partial $2
- `pay_for_event(page, context, "2")`: open the payment request, click
  `take_payment`, open the record section (`[data-qa="record_payment_button"]`),
  fill the money input ($2), choose Cash (`md-select[name='payment_method']`),
  confirm (`[data-qa="take-payment-confirmation"]`).
- `assert_event_payment_request`: state **DUE**, amount **$8.00 (out of $10.00)**,
  client **first last**, service **<event>**.
- `search_payments(..., expected_count=1)`: Payments Received filtered by "first"
  shows one `f-ellipsis-tooltip.payment-title` matching **Payment for <event>**.

## Step 2 — Full $8
- `pay_for_event(page, context, "8")` then assert state **PAID**, amount **$10.00**.
- `search_payments(..., expected_count=2)`.

## Step 3 — Receipt conversation
- `assert_cp_conversation_title(..., "Thank you for paying: Payment for <event>")`:
  open the client portal with the seeded client's portal token, open chat
  (`[data-qa="headerChatBtn"]`), assert a `[data-qa="bubble-header"]` includes the
  title.
