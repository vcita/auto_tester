# Import Excel With Tax - Script

## Frames
- Import button: frontage angular iframe (`[data-qa='action-button-products-settings-import']`).
- Import wizard: top-level POV modal (`[data-qa='import-products-modal']`).
- Products list/search/tax: inner vuetage iframe.
- `products_helpers._frame_with` resolves the holding frame for each selector.

## Actions
1. `open_import_wizard(page, context)`:
   - `page.goto("{base_url}/app/settings/products")`, wait for Import button, click it,
     wait for the wizard modal.
2. `upload_file(page, products_with_sku.xlsx)`:
   - Click `wizard-wizard-next-button` (Get started → Upload file).
   - `set_input_files` on `[data-qa='vc-dropzone--input']`.
   - Wait for the step title to become "Add taxes" (async file analysis; bounded to
     IMPORT_JOB_TIMEOUT, justified below).
3. `select_tax(page, "ImportTax", 13)`:
   - Click `[data-qa='add-taxes-listbox-ImportTax-(13%)']`, assert its `-checkbox` is
     checked, click Next, wait for the "Import" review step.
4. `submit_import(page)`:
   - Click the next button (label "Import"), wait for the "Got it" success button
     (bounded to IMPORT_JOB_TIMEOUT — import execution is async), click it, wait modal hidden.
5. `open_products_page(page, context)` — reload so the vuetage list reflects the
   import (the list loaded before the import does not auto-refresh reliably).
6. `search_products(page, "product 11", ["product 11"])` and
   `search_products(page, "sku12", ["product 12"])`:
   - Fill `[data-qa='filter-search']`, poll `.product-row .product-name` until it matches.
7. `get_product_tax(page, "product 12")`:
   - Read `[data-qa='product 12'] .product-taxes-desktop div` → "ImportTax (13%)".

## Selectors
- `[data-qa='action-button-products-settings-import']` — open wizard.
- `[data-qa='wizard-wizard-next-button']` — wizard Next / Import.
- `[data-qa='vc-dropzone--input']` — file input.
- `[data-qa='add-taxes-listbox-{name}-({rate}%)']` (+ `-checkbox`) — tax option.
- `[data-qa='wizard-step-title']` — current step (Upload file / Add taxes / Import).
- role button "Got it" — success acknowledge.
- `[data-qa='filter-search']` — product search input.
- `.product-row .product-name`, `[data-qa='{product}'] .product-taxes-desktop div`.

## Waits
- UI transitions use the 5s cap.
- File analysis (upload → Add taxes) and import execution (→ success) are genuine
  async backend jobs polled by the wizard; bounded to IMPORT_JOB_TIMEOUT (15s) and
  documented, not used to mask flaky selectors.
