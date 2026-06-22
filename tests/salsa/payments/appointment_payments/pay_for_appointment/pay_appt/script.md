# Script: Paying for appointment (partial then full)

Playwright-oriented HOW for `pay_appt`. Reuses appointment_payments_helpers.

## Preconditions (from _setup)

- Isolated account, point_of_sale denied, logged in.
- Client "first last", "display a fee" $100 service "service", appointment
  scheduled via API.

## Actions and assertions

1. `pay_for_appointment(page, context, "10", identifier="service")`
   - Opens the appointment, take payment -> record dialog -> $10 Cash -> confirm.
2. `assert_appt_payment_request(..., {state: "DUE", amount: "$90.00 (out of
   $100.00)", ...})`.
3. `search_payments(page, context, "first", "Payment for service", 1)`.
4. `pay_for_appointment(page, context, "90", identifier="service")`.
5. `assert_appt_payment_request(..., {state: "PAID", amount: "$100.00", ...})`.
6. `search_payments(page, context, "first", "Payment for service", 2)`.
