# Tips Disabled Without Gateway - Steps

## Objective
Verify the tips tab is disabled (connect-provider alert shown) when no payment provider is connected.

## Preconditions
- Logged in to the isolated account with `rollout.payments.tips_settings` enabled and
  `rollout.payments.gateway_platform` denied; no payment gateway connected.

## Steps
1. Open the tips settings tab (`/app/settings/payments?tab=tips`).
2. Verify tips settings is `disabled` (the no-gateway / connect-payment-provider alert is shown and
   the tip amount inputs are not present).

## Expected Result
- The tips tab renders the no-gateway alert; tips controls are disabled.
