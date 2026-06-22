# Changelog — Coupons in Checkout / cart_fixed

## Creation (VCITA2-13851)

Migrated `automation-js/features/salsa/coupons-pay.feature` ("Client apply cart fixed amount
coupon in cp checkout") into `tests/payments/coupons_checkout/cart_fixed`.

- API: client + two PAST appointments + a $30 entire-cart coupon (`POST /v2/coupons`).
- CP UI: pay past "appointment_1" via its "Pay" action, apply the coupon, pay via the mock
  gateway popup.
- Assertion preserved: title "Payment confirmed", subtitle "A confirmation email is on its
  way to your inbox", "Amount received: $84.00".

## Math
appointment_1 only: ($100 −$30) = $70, +20% tax = $84.00.

## Selector notes / waits
Same as cart_percentage: reused stable legacy CSS for the Vue coupon section and success
page (no product data-qa); element waits ≤5s, NAV/POPUP timeouts justified, no fixed sleeps.
