# Back-office Partial Refund Setup - Steps

## Objective
Prepare an isolated account with `point_of_sale` denied (so Quick Actions exposes the legacy Record payment dialog), then create the test client.

## Preconditions
- Runner created an isolated account and injected `username`, `password`, `auto_account`, `api_base_url` into context.
- `VCITA_ADMIN_TOKEN` is available (from `.env`).

## Steps
1. Deny the `point_of_sale` feature flag (before login) and reset the feature-flag cache.
2. Log in to the isolated account.
3. Create client `Torry Deposi` via the platform API.

## Expected Result
- After login, Quick Actions exposes `Record payment` (not POS `Take payment`); client exists.
