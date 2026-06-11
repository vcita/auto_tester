# Script: Payment confirmation emails (non-POS)

Playwright-oriented HOW for `confirmation_emails`. Reuses payments_emails_confirm
and email_api.

## Preconditions (from _setup)

- Isolated account, point_of_sale denied, logged in.
- Client "first last", suggest-to-pay $100 service "service", appointment api1,
  $10 product21 assigned to the client.

## Actions and assertions

1. `pay_appointment_with_receipt(page, context, "30", "api1")`
   - Open appointment; `take_payment` -> `record_payment_button` -> amount 30 ->
     method Cash -> ensure "Send receipt to client" checked -> confirm.
2. `wait_for_email_count(context, "Payment Confirmation", 1)`.
3. `close_client_balance(page, context, client_id, method="ACH")`
   - Open `/app/clients/{id}`; close-balance take-payment action ->
     `record_payment_button` -> method ACH -> ensure send-receipt -> confirm.
4. `wait_for_email_count(context, "Payment Confirmation", 2)`.

## Selectors / waits

- Record dialog: data-qa (`take_payment`, `record_payment_button`,
  `take-payment-confirmation`), `md-select[name='payment_method']`, send-receipt
  `md-checkbox[aria-label="Send receipt to client"]`. "Payment Confirmation" is a
  static subject (exact match). Email verified via the async bounded email log.
