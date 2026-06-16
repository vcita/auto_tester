# Test: Calendar Settings staff permissions

Migrated from `automation-js/features/tempo/calendar-settings.feature` — Scenario
"Calendar Settings Staff Permissions".

## Objective

Verify the Calendar Settings side-nav differs between the account owner (admin) and a
limited staff member.

## Preconditions

- Logged in as the account owner (subcategory `_setup`).

## Steps

1. Open the Calendar Settings page as the owner and read the side-nav layout.
2. Create a limited staff member ("Staff User", role `user`) via Platform API.
3. Switch the logged-in browser session to the staff member (SSO).
4. Open the Calendar Settings page as the staff member and read the side-nav layout.

## Expected Result

- Owner: staff selector present, 4 settings tabs.
- Limited staff: no staff selector, 3 settings tabs.
