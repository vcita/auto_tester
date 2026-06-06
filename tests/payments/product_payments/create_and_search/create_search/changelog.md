# Changelog: Create and search product

## 2026-06-06 - Initial migration (VCITA2-13858)
- Migrated from products.feature scenario 1 "Create and search product".
- Background (client + $10 product payable_item1) and the two taxes are
  API-seeded.
- Creates "product2" (price 10, cost 5, SKU 1234678, 13% tax) through the Add
  product dialog (the in-scope UI action), then asserts it is found by both name
  ("product2") and SKU ("1234678") search, each returning only [product2].
