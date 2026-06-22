# Tips Edit Persist Setup - Steps

## Objective
Prepare an isolated account where tips can be enabled: enable `rollout.payments.tips_settings`,
log in, and connect the mock payment gateway (so the tips tab is enabled).

## Preconditions
- Runner created an isolated account and injected `username`, `password`, `auto_account`,
  `api_base_url`, `base_url` into context.
- `VCITA_ADMIN_TOKEN` is available (from `.env`).

## Steps
1. Enable the `rollout.payments.tips_settings` feature flag (before login) and reset the cache.
2. Log in to the isolated account.
3. Connect the mock payment gateway via the payment providers UI.

## Expected Result
- After login a mock payment gateway is connected so the tips tab is enabled.
