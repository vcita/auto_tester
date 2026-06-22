# Script — Setup (Invoice Tax Include Mode)

`setup_invoice_tax_include`:
- `invoice_billing_setup.seed_invoice_account(page, context, with_tax=True)` (login,
  client `first last`, paid service $100, 13% tax).
- `invoice_billing_api.set_tax_mode(context, "include")` — `PUT /v2/settings`
  `{tax_mode: include}`, verified via `GET /platform/v1/payment/settings`.
