# Changelog — create_cancel_recreate

## 2026-06-03 — initial migration (VCITA2-13792)

- Migrated `automation-js/features/salsa/scheduled_payments.feature` (single
  scenario, 11 steps) into `tests/payments/scheduled_payments`.
- Structure: isolated-account subcategory with `_setup` (flags, login, client via
  API, mock gateway, credit-card enablement, saved card) and one test
  (`create_cancel_recreate`) covering the three legacy phases.
- Helpers:
  - `scheduled_payments_ui.py`: Quick Actions -> Schedule payment, client picker,
    plan dialog (name/amount/frequency + optional next-month start), success-dialog
    close, side pane open via the client card, read, and cancel.
- Reused existing helpers (no duplication): `tips_settings.tips_gateway
  .connect_mock_gateway`, `offset_fees.offset_fees_setup_ui.save_card_on_file`,
  `card_on_file.card_on_file_api.enable_credit_card`, `account_api` primitives
  (incl. `create_client`), and `_functions.login.fn_login`.
- First run: setup + Phase A passed; the rules-API filter by client id returned
  empty for the cancel uid lookup. Since the side pane already opens reliably
  through the client card, the cancel step now opens the side pane via the client
  card and cancels there (the URL+API navigation was a Selenium-era detail; the
  cancel-from-side-pane behavior is preserved), removing the API dependency.
- Waits: condition-based, capped at 5s; client-page/side-pane mount uses a 15s
  page-readiness budget; the rule uid lookup polls the rules API (eventual
  consistency). No fixed state sleeps.
