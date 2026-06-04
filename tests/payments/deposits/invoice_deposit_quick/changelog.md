# Changelog — invoice_deposit_quick

## 2026-06-04 — Initial migration (VCITA2-13795)
- Migrated deposits.feature scenario 1 (Quick-Actions record path).
- Denies point_of_sale so the Quick Actions Record-payment dialog is available.
- Records two custom payments, creates+sends an invoice with a $50 custom item, assigns
  the `Payment for deposit_item` payment as the deposit.
- Invoice identifier resolved dynamically via the invoices API (no hardcoded `#0000001`).
- Reuses the shared itemizable-dialog helpers (`add_custom_item`, `set_title`, wizard
  scopes) from estimates_helpers and the Quick-Actions/picker pattern.
