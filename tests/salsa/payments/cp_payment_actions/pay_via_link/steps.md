# pay_via_link — Client pays a service via the CP pay link

Migrates `automation-js/features/salsa/cp/payment-actions.feature`
(Scenario: "Client payment action in CP via link").

1. **Grab the pay link** for the $100 setup service. The legacy Link Builder produces a
   public make-payment URL (`vitrage /site/{uid}/make-payment?title=<service>&amount=100`);
   the editor that builds it is heavy and crash-prone in headless (VCITA2-14226), so the
   deterministic URL is used directly (same approach as the validated
   `tips_checkout_cp.open_payment_form`). Documented deviation — see changelog.
2. **Client accesses the link and pays** through the CP payment form (`#cp_iframe`):
   fill Email + First Name ("steve"), click Pay (`[data-qa='payButton']`), in the checkout
   dialog click `[data-qa="perform-payment-action"]`, submit the mock-gateway popup
   (`button[type=submit]`), wait for it to close.
   (Reuses `cp_payment_actions_helpers.pay_via_payment_form`.)
3. **Assert in the back office**: open Payments Received, search by first name "steve",
   and verify a payment whose title contains "Payment for" and the service name appears.
   (Reuses `refunds_credits.partial_refund_helpers.open_payments_received`; titles via the
   legacy `f-ellipsis-tooltip.payment-title .text` selector.)

No fixed sleeps; element waits ≤5s; NAV/popup budgets justified. data-qa selectors first.
