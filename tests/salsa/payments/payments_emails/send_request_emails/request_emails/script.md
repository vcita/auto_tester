# Script: Send payment request emails (non-POS)

Playwright-oriented HOW for `request_emails`. Reuses payments_emails_helpers,
appointment_payments_helpers (invoice_appointment), and email_api.

## Preconditions (from _setup)

- Isolated account, point_of_sale denied, logged in.
- Client "first last", require-to-pay $100 service "service" (require-to-pay so the
  appointment exposes a DUE Billing & Invoicing order row for POV-routed invoicing;
  emails are charge-type-independent), appointment api1 scheduled via API, mock
  gateway connected.

## Actions and assertions

1. `send_appointment_payment_link(page, context, "api1")`
   - Open `/app/appointments/{id}`; `take_payment` -> `setCurrentStage('send')`
     stage -> email channel (`.channel-option.email-option md-radio-button`) ->
     `take-payment-confirmation` -> Done.
2. `wait_for_email_count(context, "New payment request from ", 1, match="prefix")`.
3. `invoice_appointment(page, context, "new_invoice", "blablablabla", identifier="service")`
   - Orders-routed invoice wizard (`itemizable-details-header`, From fold billing
     address, `itemizable-dialog-main`), lands on `/app/invoices/...`.
4. `wait_for_email_count(context, "New invoice from ", 1, match="prefix")`.
5. `send_invoice_payment_link(page, context, client_id)`
   - Open latest invoice; `take_payment` -> `data-qa=send` (newTakePayment) ->
     email channel -> confirm -> Done.
6. `wait_for_email_count(context, "New payment request from ", 2, match="prefix")`.

## Selectors / waits

- Send-link: data-qa (`take_payment`, `send`, `take-payment-confirmation`),
  Angular `ng-click` stage button, channel-option radio. Email verified via the
  internal automation message log (async, bounded poll in email_api).
- Subjects are matched by prefix because the business-name suffix is the isolated
  account's dynamic name.
