# Script — Business Info Page Displays Details

## Flow
1. `get_business(context)` — read the account's business object via API:
   `business.business.name` (business name) and `business.admin_account.email` (owner email).
2. Navigate to `/app/settings/business`.
3. In the Angular iframe (`iframe[title="angularjs"]`):
   - `input[name="name"]` value == API business name.
   - `input[ng-model='owner.email']` value == API owner email.
   - `[name="country_name"] md-select-value` text == `Israel (972)`.

## Notes
- The settings page is Angular, inside `iframe[title="angularjs"]`.
- The name/email inputs are Angular property-bound, so their value must be read
  with `input_value()` (the `value` HTML attribute is empty); a short poll waits
  for Angular to populate them (no fixed sleeps).
- Country is set to Israel in the category setup via the admin API; the UI then
  renders `Israel (972)`.
- Business name/email are read from the API rather than hardcoded, since
  auto_tester names accounts dynamically (legacy hardcoded "Automation test business").
