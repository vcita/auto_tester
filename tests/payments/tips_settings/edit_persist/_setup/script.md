# Tips Edit Persist Setup - Script

## Actions
1. `enable_features(context, "rollout.payments.tips_settings")`:
   - POST `/admin/feature_flags/{user_id}/add_user_features` + reset cache.
2. `login(page, context)` with isolated account credentials.
3. `connect_mock_gateway(page, context)`:
   - `page.goto("{base_url}/app/settings/payments")`.
   - Open the payment providers item (`[data-qa="item-payment-providers"]`).
   - Click the mock provider card (`[data-qa="provider-name-mock"]`) and its connect button.
   - In the popup window, fill `#secret=bla`, `#alias=blu`, submit.
   - Save the providers dialog (`[data-qa="providers-dialog-save"]`).

## Notes
- Connecting the gateway is a setup prerequisite (not the tips feature under test), so the legacy
  UI connect flow is preserved here to produce a genuinely connected gateway; the tips behavior is
  asserted in the test.
