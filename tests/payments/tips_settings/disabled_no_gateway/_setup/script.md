# Tips Disabled Setup - Script

## Actions
1. `enable_features(context, "rollout.payments.tips_settings")`:
   - POST `/admin/feature_flags/{user_id}/add_user_features` (auth `Admin <VCITA_ADMIN_TOKEN>`).
   - GET `/infra/automation/reset_features_table_cache`.
2. `deny_features(context, "rollout.payments.gateway_platform")`:
   - POST `/admin/feature_flags/{user_id}/blacklist_user_features`.
   - GET `/infra/automation/reset_features_table_cache`.
3. `login(page, context)` with isolated account credentials.

## Why before login
- The app loads feature flags at startup; applying flags before the first login mirrors the legacy
  "set/deny flags then launch frontage" order so the tips tab reflects them on first render.
