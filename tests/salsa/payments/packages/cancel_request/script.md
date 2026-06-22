# Cancel (waive) a package payment request — Detailed Script

## Actions
1. Create a fresh client via API (`make_client`).
2. Create package `package` via API (`account_api.create_package_via_api`: specific service
   `r2p_event`, 2cr, $150) — legacy "via API" steps.
3. Assign `package` to the client via API (`account_api.assign_package_to_client`).
4. Cancel/waive the client-package payment request via UI (`cancel_request`:
   `ps-more-actions` -> `waive_payment` -> confirm `cancel_payment()`).
5. Assert client-package request: state CANCELLED, amount $150.00, client first last, package package.
   The waive -> CANCELLED propagation is eventually consistent (the BO card transiently shows
   "Payment info is not available"), so `assert_client_package` is given `client_id` and first
   confirms CANCELLED via an API read-back of the client-package's payment-request state, then
   reads the UI card once (≤2 UI retries, ≤5s each).

## Success Verification
- Client-package request is CANCELLED for $150.00.
