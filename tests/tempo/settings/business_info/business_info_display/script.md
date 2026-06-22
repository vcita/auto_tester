# Script — Business Info Page Displays Details

## Flow
1. `get_business(context)` — read the account's business object via API:
   `business.business.name` (business name) and `business.admin_account.email` (owner email).
2. Navigate to `/app/settings/business` (goto bounded at 5s).
3. Wait for the Angular iframe (`iframe[title="angularjs"]`) to boot.
4. In the Angular iframe:
   - `input[name="name"]` value == API business name.
   - `input[ng-model='owner.email']` value == API owner email.
   - `[name="country_name"] md-select-value` text == `Israel (972)`.

## Notes
- The settings page is Angular, inside `iframe[title="angularjs"]`. The iframe boot is
  a documented cross-iframe readiness exception, bounded at 10s (`IFRAME_TIMEOUT`).
- Country is set to Israel in the category setup via the admin API and **read back**
  (`wait_for_business_country`) before login, so the page never renders a stale country;
  the UI then renders `Israel (972)`.
- Business name/email are read from the API rather than hardcoded, since
  auto_tester names accounts dynamically (legacy hardcoded "Automation test business").

## Wait policy
- `goto` bounded at 5s; the Angular iframe readiness is a bounded 10s documented
  exception; all in-frame element waits are bounded at 5s.
- The name/email inputs are Angular property-bound, so their value is read with
  `input_value()` (the `value` HTML attribute is empty). `_input_value_when_ready`
  polls on a bounded <=5s loop with a 0.2s interval (poll cadence, not a blind sleep)
  until Angular populates the field.
