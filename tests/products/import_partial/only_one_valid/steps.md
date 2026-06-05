# Import Only One Valid Product - Steps

## Objective
Import an Excel file in which only one of three rows is valid, verify the review
step flags the invalid rows, and confirm only the valid product is imported.

## Preconditions
- `import_products` feature flag enabled, logged in (handled by `_setup`).

## Steps
1. Open the products settings page and launch the Import wizard.
2. Upload `products_only_one_valid.xlsx` (product 11 and 13 missing price → invalid;
   product 12 valid).
3. Continue past the Add taxes step (no tax assigned).
4. On the review step, assert at least one invalid row is flagged.
5. Import and confirm the success screen.
6. Reload the products page so the list reflects the import.
7. Search products by name `product 12` → result is exactly `product 12`.

## Expected Result
- The review step flags the invalid rows; only `product 12` is imported and found.

## Scope Source
Migrated from automation-js `features/salsa/import_products.feature` scenario
"import products from excel file that only one product is imported" (legacy asserted
error rows via `withError` and searched for the single imported product 12).
