# Changelog — Invoice In Tax Include Mode

## 2026-06-07 — Initial migration (VCITA2-13900)
- Migrated from automation-js `features/steps/invoices.feature` scenario
  "create invoice in mode include".
- Isolated US account; tax mode `include` set in `_setup`.
- Reuses `invoice_billing_ui.create_and_send_invoice` / `assert_invoice_page`.
- Assertion: invoice ISSUED at $65.00 (tax included), `product_invoice #0000001`,
  client `first last`.
