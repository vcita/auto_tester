# Changelog: Edit and cancel appointment's payment request

## 2026-06-06 - Initial migration (VCITA2-13857)

- Migrated from `automation-js/features/salsa/appointment-payments.feature`
  scenario 2 "edit and cancel appointment's payment request".
- Edits the request amount to $50 (NOT YET DUE $50.00) then waives it
  (CANCELLED $50.00), via the appointment detail page payment-status card.
