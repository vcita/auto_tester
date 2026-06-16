# Tips Edit Persist - Steps

## Objective
Verify that tips configured via API persist and render in the tips tab preview when a payment
gateway is connected.

## Preconditions
- Logged in to the isolated account with `rollout.payments.tips_settings` enabled and a mock
  payment gateway connected.

## Steps
1. Set tip options `55, 66, 77` (percent) via the settings API.
2. Reload / open the tips settings tab (`/app/settings/payments?tab=tips`).
3. Verify tips settings is `enabled` (tip amount inputs present, no no-gateway alert).
4. Verify the preview shows tip amounts `$55.00`, `$66.00`, `$77.00` (USD).

## Expected Result
- The tips tab is enabled and the preview displays the configured tip amounts.
