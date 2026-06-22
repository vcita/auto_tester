# Script: Send payment request emails via POS

Playwright-oriented HOW for `request_emails_pos`. Reuses payments_emails_helpers,
payments_emails_api (seed_extra_appointment), appointment_payments_helpers
(invoice_appointment), and email_api.

## Preconditions (from _setup)

- Isolated account, point_of_sale enabled, logged in.
- Client "first last", require-to-pay $100 service "service", appointment api1,
  mock gateway connected.

## Actions and assertions

1. `send_appointment_link_via_pos(page, context, "api1")`
   - `take_payment` opens POS; `checkout-actions-activator` ->
     `checkout-action-send` -> email channel -> `take-payment-confirmation` -> Done.
2. `wait_for_email_count(context, "New payment request from ", 1, match="prefix")`.
3. `seed_extra_appointment(context, payment_setting="require to pay", service_name="service2", identifier="api2")`
   then `invoice_appointment(page, context, "new_invoice", "blablablabla", identifier="service2")`.
4. `wait_for_email_count(context, "New invoice from ", 1, match="prefix")`.
5. `send_invoice_payment_link(page, context, client_id)`.
6. `wait_for_email_count(context, "New payment request from ", 2, match="prefix")`.

## Selectors / waits

- POS checkout: data-qa (`checkout-actions-activator`, `checkout-action-send`).
- Send-link / invoice as in scenario 1. Subjects matched by prefix (dynamic
  business-name suffix). Email verified via the async bounded email log.
