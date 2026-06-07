# Changelog: Cancel and refund paid appointment

## 2026-06-06 - Initial migration (VCITA2-13857)

- Migrated from `automation-js/features/salsa/appointment-payments.feature`
  scenario 4 "Cancel and refund paid appointment".
- point_of_sale denied; pays $100, cancels the appointment with a refund, and
  asserts CANCELLED $100.00 plus the refunded "Payment for service" payment.

## 2026-06-07 - Restore refund-detail assertion + wait audit

- `assert_payment_refunded` now opens the payment from Payments Received and
  asserts the payment detail header (shared `open_payment_detail_and_assert_title`),
  matching legacy `payment was refunded` (goToPayment + getPaymentNameText). It
  previously stopped at list-row presence.
- Wait audit (`appointment_payments_helpers.py`): replaced fixed post-action
  sleeps (`wait_for_timeout(3000/2000/1500)`) after record/cancel/complete/
  cancel-redemption with a bounded best-effort `networkidle` settle; navigation
  budgets inherited from the shared helper (10s documented). Element interactions
  stay at the 5s cap.
