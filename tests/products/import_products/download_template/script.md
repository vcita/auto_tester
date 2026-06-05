# Download Import Template - Script

## Actions
1. `open_import_wizard(page, context)` — goto products page, click Import, wait for modal.
2. `download_template(page)`:
   - `page.expect_download()` while clicking the "Download template" role button on the
     Get started step; return `download.suggested_filename`.
3. Assert the suggested filename includes `import_products` (the store downloads
   `import_products.xlsx`).
4. `close_wizard(page)` — click `[data-qa='vc-header-close-button']`.

## Selectors
- `[data-qa='import-products-modal']` — wizard modal.
- role button "Download template" — Get started step download CTA.
- `[data-qa='vc-header-close-button']` — close the wizard.

## Waits
- 5s UI cap; the download is captured via `expect_download` (no fixed sleeps).
