# Setup — CP Payment Actions (isolated account)

Mirrors the account-level prerequisites of the legacy `cp/payment-actions.feature`
Background, on a fresh isolated account.

1. Deny the `point_of_sale` feature flag (legacy non-split checkout path) via the admin
   API (`tests.account_api.deny_features`).
2. Log in to the isolated back office (UI session is needed for the mock-gateway
   connection and the back-office record-payment step).
3. Connect the mock payment gateway via the UI
   (reuses `tips_settings.tips_gateway.connect_mock_gateway`).
4. Create a "display a fee" ($100) appointment service via API
   (`account_api.create_service_via_api(charge_type="paid_non_secured", price="100")`).
   The service name is unique per run (`service<seq>`) — legacy `service+[seq]`.
5. Create a client ("first last") via API (`account_api.create_client`); capture its id
   and client-portal token.

Saves to context under `context["cp_payment_actions"]`:
`service` ({id, name}), `client` ({id, name, first, email, portal_token}).
