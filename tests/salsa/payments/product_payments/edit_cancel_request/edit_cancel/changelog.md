# Changelog: Edit and cancel product's payment request

## 2026-06-06 - Initial migration (VCITA2-13858)
- Migrated from products.feature scenario 6.
- Background (client + $10 product) and the product assignment are API-seeded.
- Edits the request to $20 (DUE) then waives it (CANCELLED) on the Product Order
  page, asserting state + amount after each, reusing product_payments_helpers.
