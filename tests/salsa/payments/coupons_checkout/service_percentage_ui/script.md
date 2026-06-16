# Script — Apply service percentage coupon (created in UI) in CP checkout

Source scenario: `automation-js/features/salsa/coupons-pay.feature`
("Client apply service percentage coupon in cp checkout" — coupon created in the UI, per
the legacy comment "using the ui and not Api").
Implementation: `test.py` + `coupons_checkout_api.py` + `coupons_checkout_cp.py`.

## API setup inside the test
- `provision_paying_client(context, services)` → client (portal JWT) + two PAST appointments.

## UI coupon creation (in scope — exercised via UI, not API)
`create_service_coupon_ui(page, "Percentage", name, "10", "appointment_1")` (Angular
Settings/Coupons, scoped via `coupons_helpers.open_coupons_settings`):
1. Click `[data-qa="action-button-coupons-new"]`.
2. Pick `md-select[name="coupon_type"]` = "Percentage"; fill `input[name="name"]`,
   `input[name="amount"]`.
3. Check `md-checkbox div.md-container.md-ink-ripple` ("on specific service"); pick the
   service in `md-select.ellipsis` = "appointment_1".
4. Click `button[ng-click="save(clientForm)"]`; read the generated code from the promote
   dialog `.description`; dismiss the dialog.

## CP UI flow (the behavior under test)
`close_balance_with_coupon(cp_page, code)`:
1. Click `a[href="#/payments/"]`, wait for `[class*=payments-list-page]`.
2. Click `.checkout-btn` (closes the whole balance: both appointments).
3. `_apply_coupon_and_pay`: `.checkout-dialog` → `.coupon-section__clickable` →
   `.v-text-field__slot input` (code) → `button.action-dialog__apply-btn` →
   `.coupon-section__applied-title` → `[data-qa="perform-payment-action"]` → mock popup
   `button[type=submit]`.

## Assertion
`assert_payment_success`: title "Payment confirmed", subtitle "A confirmation email is on
its way to your inbox", `span.paymet-text` contains "Amount received: $228.00".

## Selectors & waits
- The coupon UI is in scope and exercised through the Angular UI (not replaced by API).
  The coupon code is read from the promote dialog (legacy behavior), not via an API
  shortcut.
- data-qa used for CP menus/perform-payment/success and the coupons "new" button. The
  Angular coupon dialog fields, `md-select.ellipsis`, the promote `.description`, and the
  Vue coupon section have no data-qa; stable legacy CSS reused — data-qa should be added in
  product code.
- Element/interaction waits ≤5s; NAV_TIMEOUT (CP navigation/list readiness) and
  POPUP_TIMEOUT (mock-gateway popup) are justified non-element waits.
