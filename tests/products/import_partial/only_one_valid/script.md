# Import Only One Valid Product - Script

## Actions
1. `open_import_wizard(page, context)` — goto products page, click Import, wait for modal.
2. `upload_file(page, products_only_one_valid.xlsx)`:
   - Next (Get started → Upload), `set_input_files`, wait for "Add taxes" step
     (async file analysis, bounded to IMPORT_JOB_TIMEOUT).
3. `skip_taxes(page)` — click Next (no tax selected), wait for the "Import" review step.
4. `assert_error_rows_present(page)` — assert `.error-row-item` count > 0 (legacy `withError`).
5. `submit_import(page)` — Import, then "Got it", wait modal hidden.
6. `open_products_page(page, context)` — reload so the list reflects the import.
7. `search_products(page, "product 12", ["product 12"])`.

## Selectors
- `[data-qa='action-button-products-settings-import']`, `[data-qa='wizard-wizard-next-button']`,
  `[data-qa='vc-dropzone--input']`, `[data-qa='wizard-step-title']`.
- `.error-row-item` — review-step invalid rows.
- role button "Got it"; `[data-qa='filter-search']`, `.product-row .product-name`.

## Waits
- 5s UI cap; file analysis / import execution bounded to IMPORT_JOB_TIMEOUT (15s),
  documented async backend jobs.
