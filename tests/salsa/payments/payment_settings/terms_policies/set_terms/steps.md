# Terms and Policies - set custom terms and policies text

Migrated from `automation-js/features/salsa/payments_settings.feature` scenario 2
("Terms and Policies - set custom terms and policies text").

## Objective
Set custom text terms & policies and verify it is displayed on the payment settings page.

## Preconditions (from _setup)
- Logged in to the isolated account.
- Mock payment gateway connected.

## Steps
1. Set the terms & policies text to `terms and policies example` via the payment settings API.
2. Assert the API read-back persisted the text.
3. Navigate to the terms-and-policies settings tab and assert the textarea displays the text.
