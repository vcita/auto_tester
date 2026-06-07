# Script: Payment request created for appointment

Playwright-oriented HOW for `request_created`. Reuses appointment_payments_helpers.

## Preconditions (from _setup)

- Isolated account, logged in.
- Client "first last", "display a fee" $100 service "service", appointment
  scheduled via API (cached in `context["appointment_payments"]`).

## Actions and assertions

1. `assert_appt_payment_request(page, context, {state: "NOT YET DUE", amount:
   "$100.00", client_full_name: "first last", service_name: "service"},
   identifier="service")`
   - Navigates to `/app/appointments/{booking_id}` and reads the payment-status
     card (tolerant selectors for state/amount/service/client).
2. `cancel_appointment(page, context, identifier="service")`
   - Opens the appointment page, clicks Cancel, confirms (no refund).
3. `assert_appt_payment_request(page, context, {state: "CANCELLED", amount:
   "$100.00", client_full_name: "first last", service_name: "service",
   meeting_identifier: "this"})`
