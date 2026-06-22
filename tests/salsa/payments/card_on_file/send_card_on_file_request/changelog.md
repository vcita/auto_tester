# Changelog — Send Card on File Request

## 2026-06-01 — Initial migration (VCITA2-13757)

Migrated `automation-js/features/salsa/card-on-file.feature` (scenario: *user
sends request to add card on file*) to auto_tester.

- Setup: isolated account, client created via API, mock payment gateway connected
  via UI (reusing `tips_settings.tips_gateway.connect_mock_gateway`).
- Test: send the card-on-file request through the client's payment methods,
  assert the `Card request sent on <today>` label, and verify the
  `Confirm your preferred payment method` email via the automation inbox API.
- Replaced legacy fixed waits with condition-based waits (≤5s) and used
  `data-qa` selectors.

### Environment findings (debugging notes)

- The redesigned add-payment-method dialog (with the "Request card" segment) only
  renders when the payments rollout flags are enabled
  (`client_portal_checkout_v2`, `rollout.payments.checkout_redesign`,
  `rollout.payments.gateway_platform`). Without them the legacy simple
  "Add credit card" dialog (no request segment) shows instead.
- The card-on-file request itself is gated server-side by the `cof_invite`
  feature flag. Without it, `POST /business/payments/v1/card_requests` returns
  HTTP 422 ("The business primary payment gateway is not one of the payment
  gateways with client card on file") which surfaces in the UI as a misleading
  "Invalid email" toast. Enabling `cof_invite` makes the request succeed (201).
- The client email must not use plus-addressing in the request flow.
- The automation message inbox endpoint
  (`/infra/automation/message/content`) is directory-scoped: it requires a
  directory token (minted via `POST /platform/v1/tokens` with the admin token and
  `directory_id`), not the admin token. The runner now exposes `directory_id` in
  the test context for this.
