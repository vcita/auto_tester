# Download Import Template - Steps

## Objective
Download the products import template from the Import wizard and verify the
downloaded file name.

## Preconditions
- `import_products` feature flag enabled, logged in (handled by `_setup`).
- Runs on the same isolated account as `import_with_tax`; downloading the template
  does not depend on or affect product data.

## Steps
1. Open the products settings page and launch the Import wizard (Get started step).
2. Click "Download template" and capture the download.
3. Verify the downloaded file name includes `import_products`.
4. Close the wizard.

## Expected Result
- A file whose name includes `import_products` is downloaded.

## Scope Source
Migrated from automation-js `features/salsa/import_products.feature` scenario
"Download products import template" (asserts the downloaded file is `import_products`).
