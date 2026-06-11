# Script: Wizard - profession required (setup)

`prepare_wizard_account(page, context, business_category=None)` in
`gateway_setups_account.py`:

- `enable_wizard_flags(context)` → `enable_features` with the onboarding-wizard flags.
- No `set_business_category` call (profession must start empty).
- `fn_login(page, context, username, password)`.
