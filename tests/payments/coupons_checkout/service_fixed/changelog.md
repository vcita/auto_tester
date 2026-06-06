# Changelog — Coupons in Checkout / service_fixed

## Creation (VCITA2-13851)

Migrated `automation-js/features/salsa/coupons-pay.feature` ("Client apply service fixed
amount coupon in cp checkout") into `tests/payments/coupons_checkout/service_fixed`.

- API: client + two PAST appointments + a $20 coupon scoped to the appointment_1 service
  (`POST /v2/coupons` with `valid_services:[appointment_1.id]`).
- CP UI: close the whole balance from the payments list (`.checkout-btn`), apply the coupon,
  pay via the mock-gateway popup.
- Assertion preserved: title "Payment confirmed", subtitle "A confirmation email is on its
  way to your inbox", "Amount received: $216.00".

## Math
Whole balance, coupon scoped to appointment_1: appt_1 (($100 −$20) +20% tax = $96) +
appt_2 ($100 +20% tax = $120) = $216.00.

## Selector notes / waits
Same as the other coupons_checkout tests: reused stable legacy CSS for the Vue coupon
section and success page (no product data-qa); element waits ≤5s, NAV/POPUP timeouts
justified, no fixed sleeps.
