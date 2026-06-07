# Script: Cancel and refund paid appointment

Playwright-oriented HOW for `cancel_refund`. Reuses appointment_payments_helpers.

## Preconditions (from _setup)

- Isolated account, point_of_sale denied, logged in.
- Client "first last", "display a fee" $100 service "service", appointment
  scheduled via API.

## Actions and assertions

1. `pay_for_appointment(page, context, "100", identifier="service")` (full pay).
2. `cancel_appointment(page, context, identifier="service", refund=True)`
   - Appointment page Cancel -> tick issue-refund -> confirm.
3. `assert_appt_payment_request(..., {state: "CANCELLED", amount: "$100.00", ...})`.
4. `assert_payment_refunded(page, context, "Payment for service", "first")`
   - Payments Received filtered by "first" shows the payment row.
