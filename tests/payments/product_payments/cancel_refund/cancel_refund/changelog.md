# Changelog: Cancel and refund paid product

## 2026-06-06 - Initial migration (VCITA2-13858)
- Migrated from products.feature scenario 7.
- Background (client + $10 product) and the product assignment are API-seeded;
  point_of_sale is denied so `take_payment` opens the legacy record dialog.
- Records a $5 Cash payment, waives the request with a refund (CANCELLED $10.00),
  and verifies the refunded payment in Payments Received, reusing
  product_payments_helpers.
- The legacy "payment was refunded" check (open the payment, assert its title) is
  preserved by asserting the "Payment for payable_item1" row exists in Payments
  Received after the refund.

## 2026-06-07 - Restore refund-detail assertion

- Step 3 now opens the refunded payment from Payments Received and asserts the
  payment detail header (shared `open_payment_detail_and_assert_title`), exactly
  mirroring legacy `payment was refunded` (goToPayment + getPaymentNameText). It
  previously stopped at list-row presence.
