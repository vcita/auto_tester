# Changelog: Pay for product via Point of Sale

## 2026-06-06 - Initial migration (VCITA2-13858)
- Migrated from products.feature scenario 4b "paying for product via Point of Sale".
- Background (client + $10 product) and the product assignment are API-seeded;
  point_of_sale is enabled (account default) so `take_payment` opens POS.
- Records the payment via the POS checkout (record-payment, Cash), asserting
  PAID $10.00 and the "Payment for Sale #1 - payable_item1" row in Payments
  Received. Reuses the POS record flow pattern from event_payments_helpers.
