# Changelog: Create and search product

## 2026-06-06 - Initial migration (VCITA2-13858)
- Migrated from products.feature scenario 1 "Create and search product".
- Background (client + $10 product payable_item1) and the two taxes are
  API-seeded.
- Creates "product2" (price 10, cost 5, SKU 1234678, 13% tax) through the Add
  product dialog (the in-scope UI action), then asserts it is found by both name
  ("product2") and SKU ("1234678") search, each returning only [product2].

## 2026-06-15 - Load-tolerance for the flag-gated products page (VCITA2-14064)
- Under cumulative full-suite load the test intermittently landed on the fallback
  Billing/Taxes settings tab instead of the products list, then timed out. Root
  cause: /app/settings/products is gated by the `import_products` feature flag,
  which the session can still be serving the fallback tab for a beat after enable.
- Setup now enables `import_products` before login, and `open_products_page`
  reload-retries (<=3, 10s list wait each) until the Import action renders rather
  than failing on the first cold load. Bounded reload-retry against a real
  readiness signal, not a blanket timeout bump.
- Stress: 10/10 stable.
