# Changelog — Coupons in Checkout / cart_percentage

## Creation (VCITA2-13851)

Migrated `automation-js/features/salsa/coupons-pay.feature` ("Client apply cart percentage
coupon in cp checkout") into `tests/payments/coupons_checkout/cart_percentage`.

- API: client + two PAST appointments + a 10% entire-cart coupon (`POST /v2/coupons`).
- CP UI: pay past "appointment_1" via its "Pay" action, apply the coupon in the
  CPPaymentDialog, pay via the mock-gateway popup.
- Assertion preserved from legacy `parseCPPaymentConfirmation`: title "Payment confirmed",
  subtitle "A confirmation email is on its way to your inbox", "Amount received: $108.00".

## Math
appointment_1 only: $100 −10% = $90, +20% tax = $108.00.

## Selector notes (data-qa to add in product code)
Vue CPPaymentDialog coupon section and the success title/amount have no data-qa; reused
stable legacy CSS (`.coupon-section__clickable`, `.action-dialog__apply-btn`,
`.coupon-section__applied-title`, `.v-text-field__slot input`, `span.briliant`,
`span.thanks`, `span.paymet-text`).

## Waits
Element/interaction waits ≤5s; NAV_TIMEOUT (CP navigation/list readiness) and POPUP_TIMEOUT
(mock-gateway popup) are justified non-element waits. No fixed sleeps.
