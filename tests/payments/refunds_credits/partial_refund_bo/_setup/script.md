# Back-office Partial Refund Setup - Script

## Actions
1. `prepare_account(page, context, deny_pos=True)`:
   - POST `/admin/feature_flags/{user_id}/blacklist_user_features` with `features=point_of_sale` (auth `Admin <VCITA_ADMIN_TOKEN>`).
   - GET `/infra/automation/reset_features_table_cache`.
   - `fn_login` with isolated account credentials (flags fetched fresh on first load).
   - POST `/platform/v1/clients` (first `Torry`, last `Deposi`).

## Why deny before login
- The app loads feature flags at startup. Denying after login leaves the UI on cached flags, so denial must happen before the first login (mirrors the legacy "deny then launch frontage" order).

## Context Updates
- `created_client_id`, `created_client_name`, `created_client_email`.
