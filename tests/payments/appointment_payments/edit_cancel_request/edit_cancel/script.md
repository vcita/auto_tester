# Script: Edit and cancel appointment's payment request

Playwright-oriented HOW for `edit_cancel`. Reuses appointment_payments_helpers.

## Preconditions (from _setup)

- Isolated account, logged in.
- Client "first last", "display a fee" $100 service "service", appointment
  scheduled via API.

## Actions and assertions

1. `edit_appt_payment_amount(page, context, "50", identifier="service")`
   - Opens the appointment, opens the payment-status more-actions menu, clicks
     Edit, sets price to 50, saves.
2. `assert_appt_payment_request(..., {state: "NOT YET DUE", amount: "$50.00",
   client_full_name: "first last", service_name: "service"}, identifier="service")`
3. `cancel_appt_payment_request(page, context, identifier="service")`
   - More-actions -> Waive payment -> confirm (no refund).
4. `assert_appt_payment_request(..., {state: "CANCELLED", amount: "$50.00", ...})`
