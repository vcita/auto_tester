# pay_via_link — Detailed script

Source: `tests/salsa/payments/cp_payment_actions/pay_via_link/steps.md`
Migrated from `automation-js/features/salsa/cp/payment-actions.feature` (Scenario 1).

## Preconditions (from _setup)
`context["cp_payment_actions"]["service"]` = the "display a fee" $100 service.

## Steps
1. `pay_via_payment_form(page, context, pay_for=<service.name>, amount="100",
   first_name="steve", email="test3+<ms>@vmeetme.com")`
   - Opens a fresh CP browser context on the public make-payment URL (the "pay link").
   - Fills Email + First Name, clicks Pay, proceeds in the checkout dialog, submits the
     mock-gateway popup, waits for it to close. CP context is closed in `finally`.
2. `assert_payment_in_search(page, first_name="steve",
   expected_substrings=["Payment for", <service.name>])`
   - Opens Payments Received in the back office, searches by "steve", and asserts a payment
     title contains both "Payment for" and the service name (legacy expected
     "Payment for service [seq]").

## Selectors / waits
- Pay form + popup + success reuse `cp_payment_actions_helpers` (CP_IFRAME, payButton,
  perform-payment-action, mock submit) — proven in coupons_checkout / tips_checkout.
- BO search reuses `open_payments_received`; titles via `f-ellipsis-tooltip.payment-title .text`.
- Element waits ≤5s; CP nav + popup use the documented longer budget; bounded re-check on
  the async-propagating BO list. No fixed sleeps for actions.
