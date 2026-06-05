# Excel Import Setup - Script

## Actions
1. `enable_features(context, "import_products")`:
   - POST `/admin/feature_flags/{user_id}/add_user_features` + reset cache.
2. `create_tax_via_api(context, "ImportTax", 13)`:
   - POST `/business/payments/v1/taxes` `{tax:{name,rate,default_for_categories:[]}, new_api:true}`
     (the endpoint the legacy `api/tax.js` and the product tax flow use).
   - Stores `import_tax_name` / `import_tax_rate` in context for the test.
3. `login(page, context)` with isolated account credentials.

## Notes
- Tax creation is a setup prerequisite (not the import behavior under test), so it is
  done via API. The tax is still selected and asserted through the UI in the test.
- The legacy Background also created a client; it is never used or asserted by any
  scenario, so it is intentionally omitted (no coverage loss).
