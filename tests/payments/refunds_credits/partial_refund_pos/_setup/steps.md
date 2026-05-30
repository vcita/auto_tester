# POS Partial Refund Setup - Steps

## Objective
Prepare an isolated account (default flags, Point of Sale enabled) and create the test client.

## Preconditions
- Runner created an isolated account and injected `username`, `password`, `auto_account`, `api_base_url` into context.

## Steps
1. Log in to the isolated account.
2. Create client `Torry Deposi` via the platform API.

## Expected Result
- Dashboard is reachable; client exists and is stored in context as `created_client_name`.
