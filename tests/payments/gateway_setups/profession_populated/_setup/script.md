# Script: Wizard - populated profession (setup)

`prepare_wizard_account(page, context, business_category="legal_services")` in
`gateway_setups_account.py`:

- `enable_wizard_flags(context)` → `enable_features` with the onboarding-wizard flags.
- `set_business_category(context, "legal_services")` → admin POST
  `/platform/v1/businesses/{uid}` with `{business:{business:{business_category}}}`,
  confirmed by a GET read-back.
- `fn_login(page, context, username, password)`.
