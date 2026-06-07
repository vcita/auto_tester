# Script: Wizard - funnel v1 upgrade (setup)

`prepare_wizard_account(page, context, business_category="legal_services", funnel_v1=True)`
in `gateway_setups_account.py`:

- `enable_wizard_flags(context, funnel_v1=True)` → `enable_features` with the wizard flags
  plus `vp_payment_conversion_one,payment_gateways_disabled`.
- `set_business_category(context, "legal_services")` (admin POST + read-back).
- `fn_login(page, context, username, password)`.
