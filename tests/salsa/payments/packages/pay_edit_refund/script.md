# Pay, edit and complete an any-service package request — Detailed Script

## Actions
1. Deny `point_of_sale` via API (`account_api.deny_features`) so payments use the record dialog.
2. Create a fresh client via API (`make_client`).
3. Create package `bundle1` via UI (`create_package`, any service `service`+`r2p_event`,
   5cr, $150).
4. Assign `bundle1` to the client via the client card (`assign_package_via_client_card`).
5. Pay $10 (`record_package_payment`, reused) -> assert DUE `$140.00 (out of $150.00)`.
6. Edit the request amount to $50 (`edit_request_amount`) -> assert DUE `$40.00 (out of $50.00)`.
7. Pay $40 (`record_package_payment`) -> assert PAID `$50.00`.
8. Assert two "Payment for bundle1 - Package purchased" in Payments Received
   (`assert_payment_count_in_search`, expected_count=2).

> Each DUE/PAID assert (steps 5-7) follows a pay/edit action whose state propagation is
> eventually consistent (the BO card transiently shows "Payment info is not available"), so
> `assert_client_package` is given `client_id` and first confirms the target state via an API
> read-back of the client-package's payment-request state, then reads the UI card once (≤2 UI
> retries, ≤5s each).

## Success Verification
- Partial pay + edited request + final PAID, with two recorded payments.
