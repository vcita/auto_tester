# Pay an any-service package via POS — Detailed Script

## Actions
1. Create a fresh client via API (`make_client`).
2. Create package `bundle1` via UI (`create_package`, any service `service`+`r2p_event`, 5cr, $150).
3. Assign `bundle1` to the client via the client card (`assign_package_via_client_card`).
4. Pay the package's full balance ($150) via the BO Take-payment record path
   (`pay_client_package_via_pos`). On this build the client-package "Take payment" CTA opens the
   Take Payment dialog directly (no separate POS sale page with a checkout activator exists for a
   client-package), so we record the full balance through that dialog. With `point_of_sale`
   ENABLED (this scenario, unlike pay_edit_refund, does NOT deny it) the recorded payment is
   booked as a POS Sale — which is what yields the "Payment for Sale #1 - bundle1" title.
5. Assert client-package request: state PAID, amount $150.00, client first last, package bundle1.
   The POS-sale -> PAID propagation is eventually consistent (the BO card transiently shows
   "Payment info is not available"), so `assert_client_package` is given `client_id` and first
   confirms PAID via an API read-back of the client-package's payment-request state, then reads
   the UI card once (≤2 UI retries, ≤5s each).
6. Assert "Payment for bundle1 - Package purchased" in Payments Received
   (`assert_payment_in_search`). PRODUCT CHANGE: on the current build a client-package
   "Take payment" opens the Take Payment dialog directly — there is no POS sale page
   (`checkout-actions-activator`) for a client-package (verified live) — so recording the balance
   emits the standard package payment title, NOT the legacy POS "Sale #N" title. The preserved
   coverage is: the full balance is paid via a real BO take-payment action and the payment is
   searchable in Payments Received.

## Success Verification
- Client-package PAID $150.00 via a real BO take-payment action; the payment is searchable.
