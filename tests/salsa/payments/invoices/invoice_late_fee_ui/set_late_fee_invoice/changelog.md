# Changelog - set_late_fee_invoice

## 2026-06-08 - Initial migration (VCITA2-13991)
- Migrated from `automation-js/features/steps/payments-settings/invoice-settings.feature`
  scenario "Set up invoice late fee" (full UI + client-portal parity).
- New helpers:
  - `late_fee_settings_ui.set_amount_late_fee` / `assert_late_fee_enabled` — set
    amount-based late fees through the Billing & Invoicing settings UI (legacy lateFee.js).
  - `invoice_cp_ui.open_portal` / `open_pending_invoice` / `assert_cp_invoice` — open the
    client portal as the client and verify the invoice's "Late fees" caption (legacy CP
    dashboard/paymentsList/invoice page objects).
- Reused `invoice_billing_ui.create_and_send_invoice` (extended with an additive
  `enable_late_fee` toggle mirroring legacy setLateFeeCheckbox) and `assert_invoice_page`
  (with the `late_fee="Subject to late fees"` caption).
- Setup uses `account_api.create_client` to capture the portal token (the shared
  `seed_invoice_account` does not), plus a `display a fee` service ($100). US account.
- Quality: adds a late-fee settings persistence re-check beyond the legacy save toast.
