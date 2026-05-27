# EU Strict Invoices Teardown - Script

## Actions
- Remove context keys created by the isolated EU strict invoice setup and test.
- Account deletion is handled by the runner because the subcategory declares `account_profile.cleanup: always`.

## Success Verification
- Context no longer contains keys with prefixes used by the EU strict invoice flow.
