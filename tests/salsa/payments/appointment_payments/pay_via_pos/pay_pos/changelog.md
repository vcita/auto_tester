# Changelog: Paying for appointment via Point of Sale

## 2026-06-06 - Initial migration (VCITA2-13857)

- Migrated from `automation-js/features/salsa/appointment-payments.feature`
  scenario 3b "paying for appointment via Point of Sale".
- point_of_sale enabled; records the require-to-pay request through POS and
  asserts PAID $100.00 plus the "Payment for Sale #1 - service-rtp" payment.
