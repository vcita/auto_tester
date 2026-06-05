# Changelog - Import Only One Valid Product

## 2026-06-05 - Initial migration (VCITA2-13797)
- Migrated from automation-js `features/salsa/import_products.feature` scenario
  "import products from excel file that only one product is imported".
- Validated live on integration (Playwright): uploading `products_only_one_valid.xlsx`
  shows "1 of 3 products ready" with 2 flagged invalid rows (`.error-row-item`).
- Preserves the legacy `withError` assertion (invalid rows flagged) and the
  search assertion (only product 12 imported).
- Runs on its own isolated account so product 12 here never collides with the
  import_products scenario's product 12.

## 2026-06-05 - Structure + stability
- Moved to `tests/products/import_partial` (isolated subcategory directly under
  the `products` top category) so a full `products` run reaches it — the runner
  only descends into isolated subcategories that are direct children of a top
  category, not grandchildren.
- Inherits the shared `products_helpers` atomic-name-read fix; products stress
  12/12 (100%).
