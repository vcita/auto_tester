# Script — Apply cart percentage coupon in CP checkout

Source scenario: `automation-js/features/salsa/coupons-pay.feature`
("Client apply cart percentage coupon in cp checkout").
Implementation: `test.py` + `coupons_checkout_api.py` + `coupons_checkout_cp.py`.

## API setup inside the test
- `provision_paying_client(context, services)` → `POST /platform/v1/clients` (captures the
  portal JWT) + two `POST /business/scheduling/v1/bookings` with a PAST start_time
  (legacy `previous_month_10`, 10:00 America/New_York → UTC).
- `create_coupon_via_api(context, name, "percent", "10")` → `POST /v2/coupons`
  {coupon_type:"percent", amount:"10", starts_at:yesterday, expires_at:+1y,
  valid_services:null}. Returns the coupon code.

## CP UI flow (the behavior under test)
`open_portal` opens a fresh browser context at
`{CP_VITRAGE}/site/{pivot}/action?client_jwt={token}` (CP renders in `#cp_iframe`).
`pay_meeting_with_coupon(cp_page, "appointment_1", code)`:
1. Click `[data-qa='client-area-menu-bookings']`, wait for `.booking-title`.
2. Click `[data-qa="tab-selector-past"]`.
3. Click the `.booking-list-item.list-item` filtered by "appointment_1", wait for `.booking-page`.
4. Click the `.action.v-btn .v-btn__content` whose text is "Pay".
5. `_apply_coupon_and_pay`: wait `.checkout-dialog`; click `.coupon-section__clickable`;
   fill `.v-text-field__slot input` with the code; click `button.action-dialog__apply-btn`;
   wait `.coupon-section__applied-title`; click `[data-qa="perform-payment-action"]`
   (opens the mock-gateway popup); submit `button[type=submit]`; wait for popup close.

## Assertion
`assert_payment_success` (in `#cp_iframe`): `[data-qa='payment-success-page']` visible;
`span.briliant` contains "Payment confirmed"; `span.thanks` contains "A confirmation email
is on its way to your inbox"; `span.paymet-text` contains "Amount received: $108.00".

## Selectors & waits
- data-qa used for menus/tabs/perform-payment/success page. The Vue coupon section
  (`.coupon-section__*`, `.action-dialog__apply-btn`, `.v-text-field__slot input`) and the
  success title/amount (`span.briliant`/`span.thanks`/`span.paymet-text`) have no data-qa;
  stable legacy CSS is reused — data-qa should be added in product code.
- Element/interaction waits ≤ 5s. The longer budgets are NAV_TIMEOUT (CP navigation / list
  render readiness) and POPUP_TIMEOUT (external mock-gateway popup round trip) — justified
  navigation/popup readiness, not element-interaction waits.
