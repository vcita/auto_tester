# Script — Apply service fixed-amount coupon in CP checkout

Source scenario: `automation-js/features/salsa/coupons-pay.feature`
("Client apply service fixed amount coupon in cp checkout").
Implementation: `test.py` + `coupons_checkout_api.py` + `coupons_checkout_cp.py`.

## API setup inside the test
- `provision_paying_client(context, services)` → client (portal JWT) + two PAST appointments.
- `create_coupon_via_api(context, name, "fixed", "20", valid_services=[appointment_1.id])`
  → `POST /v2/coupons` scoping the coupon to the appointment_1 service. Returns the code.

## CP UI flow (the behavior under test)
`close_balance_with_coupon(cp_page, code)`: open `a[href="#/payments/"]` → wait
`[class*=payments-list-page]` → click `.checkout-btn` (closes the whole balance) →
`_apply_coupon_and_pay` (`.checkout-dialog` → `.coupon-section__clickable` →
`.v-text-field__slot input` → `button.action-dialog__apply-btn` →
`.coupon-section__applied-title` → `[data-qa="perform-payment-action"]` → mock popup
`button[type=submit]`).

## Assertion
`assert_payment_success`: title "Payment confirmed", subtitle "A confirmation email is on
its way to your inbox", `span.paymet-text` contains "Amount received: $216.00".

## Selectors & waits
Same policy as the other coupons_checkout tests (data-qa first; stable legacy CSS for the
Vue coupon section/success page; element waits ≤5s; NAV/POPUP timeouts justified).
