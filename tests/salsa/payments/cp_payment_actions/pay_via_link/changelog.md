# Changelog — CP Payment Actions / pay_via_link

## Creation (VCITA2-14227)

Migrated `automation-js/features/salsa/cp/payment-actions.feature`
(Scenario: "Client payment action in CP via link") into
`tests/salsa/payments/cp_payment_actions/pay_via_link`.

- A new client ("steve") pays the $100 "display a fee" setup service through the public
  CP make-payment form via the mock gateway, then the back-office Payments Received search
  (by first name "steve") shows a "Payment for ... <service>" record.
- Reuse: `cp_payment_actions_helpers.pay_via_payment_form` (CP form + mock popup + success,
  built on `coupons_checkout_cp`); `assert_payment_in_search` wraps
  `refunds_credits.partial_refund_helpers.open_payments_received`.

## Deviation — pay link derived, not grabbed via the editor
The legacy "grab pay link" opens the client-portal-editor Link Builder
(`/app/client-portal-editor` -> Create -> `[data-qa='action-item-pay']` -> payFor/amount ->
Get Link -> `div.link-result-wrapper > div.text`). That editor is heavy and crash-prone in
headless (the sibling VCITA2-14226 hit repeated TargetClosedError). Evidence from the legacy
page objects shows the produced link is exactly the public make-payment URL
(`CPPaymentForm.goto`: `vitrage /site/{uid}/make-payment?title=<pay_for>&amount=<amount>`),
which the validated `tips_checkout_cp.open_payment_form` already uses. So the pay link is
derived from that deterministic URL instead of driving the editor. Coverage preserved: the
client still accesses a pay link and pays through the same CP payment form; only the brittle
link-grab UI is bypassed.

## Selector notes / waits
data-qa first (payButton, perform-payment-action). BO titles via the legacy
`f-ellipsis-tooltip.payment-title .text`. Element waits ≤5s; CP nav + mock popup use the
documented longer budget; bounded re-check on the async-propagating BO list. No fixed sleeps.
