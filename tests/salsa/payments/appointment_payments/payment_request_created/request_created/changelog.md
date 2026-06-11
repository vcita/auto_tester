# Changelog: Payment request created for appointment

## 2026-06-06 - Initial migration (VCITA2-13857)

- Migrated from `automation-js/features/salsa/appointment-payments.feature`
  scenario 1 "payment request created for appointment".
- Setup seeds the client, a "display a fee" $100 service, and an API-scheduled
  appointment.
- Asserts NOT YET DUE $100.00, cancels the appointment, asserts CANCELLED
  $100.00 via the appointment detail page payment-status card.
