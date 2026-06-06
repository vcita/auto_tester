# Changelog: Cancel and refund paid appointment

## 2026-06-06 - Initial migration (VCITA2-13857)

- Migrated from `automation-js/features/salsa/appointment-payments.feature`
  scenario 4 "Cancel and refund paid appointment".
- point_of_sale denied; pays $100, cancels the appointment with a refund, and
  asserts CANCELLED $100.00 plus the refunded "Payment for service" payment.
