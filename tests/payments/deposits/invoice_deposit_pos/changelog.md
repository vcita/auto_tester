# Changelog — invoice_deposit_pos

## 2026-06-04 — Initial migration (VCITA2-13795)
- Migrated deposits.feature scenario 2 (POS record path).
- Uses point_of_sale (enabled by default); runs before invoice_deposit_quick, which
  denies POS for the shared isolated account.
- Records two POS custom-item sales, creates+sends an invoice with a $50 custom item,
  assigns the "Payment for Sale #1 - deposit_item" sale payment as the deposit.
- Reuses the invoice + deposit helpers from deposits_invoice_ui; POS flow in
  deposits_pos_ui. Invoice resolved dynamically via the invoices API.
