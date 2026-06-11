# Script: Payment confirmation emails via POS

Playwright-oriented HOW for `confirmation_emails_pos`. Reuses payments_emails_confirm
and email_api.

## Preconditions (from _setup)

- Isolated account, point_of_sale enabled, logged in.
- Client "first last", require-to-pay $100 service "service", appointment api1,
  $10 product21 assigned to the client.

## Actions and assertions

1. `record_appointment_via_pos(page, context, "api1")`
   - Open appointment; `take_payment` opens POS; `checkout-actions-activator` ->
     `checkout-action-record` -> method Cash -> ensure send-receipt -> confirm.
2. `wait_for_email_count(context, "Payment Confirmation", 1)`.
3. `record_for_client_via_pos(page, context, "first last")`
   - Quick Actions -> `VcLargeQuickAction-point_of_sale` -> select client -> add all
     open requests (`.client-details-container [role="alert"] [type="button"]`) ->
     checkout -> record -> Cash -> ensure send-receipt -> confirm.
4. `wait_for_email_count(context, "Payment Confirmation", 2)`.

## Selectors / waits

- POS: data-qa (`checkout-actions-activator`, `checkout-action-record`,
  `VcLargeQuickAction-point_of_sale`), client picker (`div.search-clients input`),
  add-open-requests alert button. "Payment Confirmation" exact subject. Email
  verified via the async bounded email log.
