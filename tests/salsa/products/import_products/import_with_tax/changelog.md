# Changelog - Import Excel With Tax

## 2026-06-05 - Initial migration (VCITA2-13797)
- Migrated from automation-js `features/salsa/import_products.feature` scenario
  "import products from excel flie".
- Flow validated live on integration before coding (Playwright): open wizard →
  Next → upload `products_with_sku.xlsx` → auto-advance to Add taxes → select
  `ImportTax (13%)` → Next → Import → "Got it".
- Assertions preserved from legacy: search by name (`product 11`), search by SKU
  (`sku12` → `product 12`), product 12 tax = `ImportTax (13%)`.
- Tax created via API in `_setup` (prerequisite), selected + asserted via UI.
- Waits: 5s UI cap; upload→AddTaxes and import→success bounded to 15s as
  documented async backend jobs.

## 2026-06-05 - Stability fix (stress 8/10 → 12/12)
- Root cause of intermittent `TimeoutError: 5000ms`: `_product_names` read rows
  with `count()` + per-row `nth().inner_text()`. While the product list
  re-rendered (e.g. 3 rows → 1 after a search), a row detached between the two
  calls and `inner_text()` blocked for the full default timeout.
- Fix: read all visible names atomically via `all_inner_texts()` (no per-element
  actionability wait), and re-acquire + retry the search `fill` (≤2 retries,
  2s each) since the search input is also re-rendered on result changes.
- Result: products stress 12/12 (100%), stamped stable.
