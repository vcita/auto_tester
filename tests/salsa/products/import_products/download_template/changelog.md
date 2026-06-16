# Changelog - Download Import Template

## 2026-06-05 - Initial migration (VCITA2-13797)
- Migrated from automation-js `features/salsa/import_products.feature` scenario
  "Download products import template".
- Validated live on integration (Playwright): the wizard "Download template" button
  downloads `import_products.xlsx`; assertion checks the name includes `import_products`.
- Co-located on the `excel_import` isolated account (download is independent of
  product data), saving one account creation vs. a separate isolated subcategory.
- Download captured via `expect_download` within the 5s UI cap; no fixed sleeps.
