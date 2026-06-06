# Changelog: Pay for product

## 2026-06-06 - Initial migration (VCITA2-13858)
- Migrated from products.feature scenario 4 "paying for product".
- Background (client + $10 product) and the product assignment are API-seeded;
  point_of_sale is denied so `take_payment` opens the legacy record dialog.
- Records a $2 then $8 Cash payment on the Product Order page, asserting
  DUE $8.00 (out of $10.00) -> PAID $10.00, the order listing, and the matching
  Payments Received rows after each payment.
- Reuses the entity-agnostic record-payment / orders / payments helpers from
  event_payments_helpers via product_payments_helpers.
