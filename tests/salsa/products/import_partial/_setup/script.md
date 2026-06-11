# Partial Import Setup - Script

## Actions
1. `enable_features(context, "import_products")`:
   - POST `/admin/feature_flags/{user_id}/add_user_features` + reset cache.
2. `login(page, context)` with isolated account credentials.

## Notes
- The legacy Background also created a tax and a client; neither is exercised by
  this scenario (it imports without assigning a tax and never touches a client),
  so both are intentionally omitted (no coverage loss).
