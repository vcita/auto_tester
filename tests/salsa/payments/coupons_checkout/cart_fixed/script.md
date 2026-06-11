# Script — Apply cart fixed-amount coupon in CP checkout

Source scenario: `automation-js/features/salsa/coupons-pay.feature`
("Client apply cart fixed amount coupon in cp checkout").
Implementation: `test.py` + `coupons_checkout_api.py` + `coupons_checkout_cp.py`.

## API setup inside the test
- `provision_paying_client(context, services)` → client (portal JWT) + two PAST appointments.
- `create_coupon_via_api(context, name, "fixed", "30")` → `POST /v2/coupons`
  {coupon_type:"fixed", amount:"30", valid_services:null}. Returns the coupon code.

## CP UI flow (the behavior under test)
Identical to `cart_percentage`: `pay_meeting_with_coupon(cp_page, "appointment_1", code)`
opens Bookings → Past → "appointment_1" → "Pay", applies the coupon in `.checkout-dialog`,
and pays through the mock-gateway popup. See that script for the selector list.

## Assertion
`assert_payment_success`: title "Payment confirmed", subtitle "A confirmation email is on
its way to your inbox", `span.paymet-text` contains "Amount received: $84.00".

## Selectors & waits
Same policy as `cart_percentage` (data-qa first; stable legacy CSS for the Vue coupon
section/success page; element waits ≤5s; NAV/POPUP timeouts justified).
