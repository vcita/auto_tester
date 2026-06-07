# Script — Setup (Invoice Late Fee)

`setup_invoice_late_fee`:
- `invoice_billing_setup.seed_invoice_account(page, context, with_tax=True)`.
- `invoice_billing_api.set_late_fee_settings(enabled=True, amount="10", percent="10",
  fee_type="percent", days="5")` → `PUT /v2/settings`
  `{late_fees_settings: {...}}`.
