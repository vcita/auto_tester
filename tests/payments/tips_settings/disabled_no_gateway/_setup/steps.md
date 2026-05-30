# Tips Disabled Setup - Steps

## Objective
Prepare an isolated account where the tips tab is reachable but no payment provider can be
connected: enable `rollout.payments.tips_settings` and deny `rollout.payments.gateway_platform`,
then log in.

## Preconditions
- Runner created an isolated account and injected `username`, `password`, `auto_account`,
  `api_base_url`, `base_url` into context.
- `VCITA_ADMIN_TOKEN` is available (from `.env`).

## Steps
1. Enable the `rollout.payments.tips_settings` feature flag (before login) and reset the cache.
2. Deny the `rollout.payments.gateway_platform` feature flag and reset the cache.
3. Log in to the isolated account (flags are read fresh on first app load).

## Expected Result
- After login the account can open the tips tab, but no payment gateway is/can be connected.
