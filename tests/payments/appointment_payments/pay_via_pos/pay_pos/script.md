# Script: Paying for appointment via Point of Sale

Playwright-oriented HOW for `pay_pos`. Reuses appointment_payments_helpers.

## Preconditions (from _setup)

- Isolated account, point_of_sale enabled, logged in.
- Client "first last", "require to pay" $100 service "service-rtp", appointment
  scheduled via API.

## Actions and assertions

1. `record_appt_payment_via_pos(page, context, identifier="service-rtp")`
   - Opens the appointment, take payment -> POS checkout -> Record payment ->
     Cash -> confirm.
2. `assert_appt_payment_request(..., {state: "PAID", amount: "$100.00",
   client_full_name: "first last", service_name: "service-rtp"})`.
3. `search_payments(page, context, "first", "Payment for Sale #1 - service-rtp", 1)`.
