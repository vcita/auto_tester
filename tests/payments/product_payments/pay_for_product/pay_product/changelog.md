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

## 2026-06-07 - Exact order/payment counts + wait audit

- `assert_order_listed` now applies the Billing & Invoicing **products** order-type
  filter before asserting the row, mirroring legacy `search orders | filter |
  products`. Payments Received counts are exact (1 then 2) via the shared
  exact-count `search_payments`.
- Wait audit (`product_payments_helpers.py`): replaced fixed post-action sleeps
  (`wait_for_timeout(3000/2500/2000/1500)`) after record/cancel/edit/create/assign
  with a bounded best-effort `networkidle` settle; reduced the add-product dialog
  retry loop from 4 to 3 attempts (<=2 retries). Navigation budgets inherited from
  the shared helper (documented 10s); element interactions stay at the 5s cap.
