# Changelog — Create With Items And Copy Invoice

## 2026-06-07 — Initial migration (VCITA2-13900)
- Migrated from automation-js `features/steps/invoices.feature` scenario
  "create invoice with new and existing items, and copy invoice".
- Isolated US account (invoice numbering must start at #0000001).
- Reuses the shared POV itemizable wizard helpers from
  `tests/sales/estimates/estimates_helpers.py` (same dialog as estimates) via new
  `invoice_billing_ui.create_and_send_invoice` / `copy_invoice` / `search_orders` /
  `assert_invoice_page`.
- API setup (client, paid "display a fee" service, 13% tax) via
  `invoice_billing_setup.seed_invoice_account`.
- Assertions: invoice detail (#0000001 / ISSUED / $66.95 / first last) and the exact
  ordered orders list after each create + copy step.
