# Import Excel With Tax - Steps

## Objective
Import a list of products from an Excel file, assign a tax during import, and
verify the imported products are searchable (by name and SKU) with the tax applied.

## Preconditions
- `import_products` feature flag enabled, a tax (`ImportTax` 13%) created, logged in
  (handled by `_setup`).

## Steps
1. Open the products settings page and launch the Import wizard.
2. Upload `products_with_sku.xlsx` (3 valid products: product 11/12/13).
3. On the Add taxes step, select the `ImportTax (13%)` tax.
4. Import the products and confirm the success screen.
5. Reload the products page so the list reflects the import.
6. Search products by name `product 11` → result is exactly `product 11`.
7. Search products by SKU `sku12` → result is exactly `product 12`.
8. Verify `product 12` shows the tax `ImportTax (13%)`.

## Expected Result
- All 3 products import; search by name and by SKU return the expected single
  product; product 12 carries the assigned tax.

## Scope Source
Migrated from automation-js `features/salsa/import_products.feature` scenario
"import products from excel flie".
