# POS Partial Refund Setup - Script

## Actions
1. `prepare_account(page, context, deny_pos=False)`:
   - `fn_login` with isolated account credentials.
   - POST `/platform/v1/clients` (first `Torry`, last `Deposi`).

## Context Updates
- `created_client_id`, `created_client_name`, `created_client_email`.
