# Changelog — Coupons in Checkout / service_percentage_ui

## Creation (VCITA2-13851)

Migrated `automation-js/features/salsa/coupons-pay.feature` ("Client apply service
percentage coupon in cp checkout") into
`tests/payments/coupons_checkout/service_percentage_ui`.

- Coupon creation is performed via the Angular Settings/Coupons UI (legacy used the UI
  here, not the API — preserved on purpose). `create_service_coupon_ui` reuses the existing
  `coupons_helpers` selectors/scope and adds the "on specific service" checkbox + service
  select, then reads the generated code from the promote dialog `.description`.
- API: client + two PAST appointments.
- CP UI: close the whole balance from the payments list (`.checkout-btn`), apply the coupon,
  pay via the mock-gateway popup.
- Assertion preserved: title "Payment confirmed", subtitle "A confirmation email is on its
  way to your inbox", "Amount received: $228.00".

## Math
Whole balance, coupon scoped to appointment_1: appt_1 ($100 −10% +20% tax = $108) +
appt_2 ($100 +20% tax = $120) = $228.00.

## Selector notes (data-qa to add in product code)
Angular coupon dialog fields, `md-select.ellipsis`, the promote `.description`, and the Vue
CPPaymentDialog coupon section have no data-qa; reused stable legacy CSS.

## Waits
Element/interaction waits ≤5s; NAV/POPUP timeouts justified non-element waits; no fixed sleeps.
