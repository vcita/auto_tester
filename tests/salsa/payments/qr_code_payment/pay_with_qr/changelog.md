# Changelog: pay_with_qr

## 2026-06-06 — Initial migration (VCITA2-13850)
- Migrated `automation-js/features/salsa/qr-code-payment.feature` (scenario "pay with QR code")
  into `tests/payments/qr_code_payment` as a NEW isolated-account subcategory under `payments`.
- Setup (`_setup/test.py:setup_qr_code_payment`): enable `client_portal_checkout_v2` BEFORE login
  (feature flags are read into the session at login; the POS "Pay with QR code" action is gated by
  this flag), log in, create client `first last` and the paid service `service-pay+<ts>`
  (`charge_type=paid_non_secured`, price 100 — legacy "display a fee") via API.
- Extended `tests/account_api.create_service_via_api` with optional `charge_type`/`price` kwargs
  (defaults preserve existing free-service callers).
- Helpers (`qr_code_payment_helpers.py`):
  - `grab_qr_link`: POS via Quick Actions -> point_of_sale -> client picker -> add service catalog
    item (hover + `add-item`) -> checkout -> `checkout-action-qr` -> read `.payment-content`
    `data-link`. Reuses `_find_control/_require/_select_client/QUICK_ACTIONS_BUTTON` (deposits_invoice_ui)
    and `TAKE_PAYMENT_ITEM` (deposits_pos_ui).
  - `pay_via_link`: pay the grabbed link in a fresh browser context (the "another tab"); raise the
    active dialog z-index, proceed (`.continue-btn`) -> mock popup `button[type=submit]` -> success
    page (`.done-loading[data-qa='payment-success-page']` + `span.briliant`).
  - `assert_qr_dialog_success`: poll back-office `[data-qa='payment-received']` then `vc-footer-Done`.
  - `assert_payment_page`: `open_payment_by_name` (partial_refund_helpers) + billing iframe scope;
    assert name, amount ($100.00), type (Credit Card (Online)), and items ([service]).
- Reused `connect_mock_gateway` (tips_gateway) for the mock-gateway prerequisite.
- Waits: element/dialog/state <= 5s; only the public link-page nav (`NAV_TIMEOUT`) and the external
  mock-gateway round-trip + payment propagation (`PAYMENT_PROPAGATE_TIMEOUT`) use 20s
  eventual-consistency budgets; no fixed sleeps; retries <= 2.
- Registered `qr_code_payment` in `tests/payments/_category.yaml` execution_order.
