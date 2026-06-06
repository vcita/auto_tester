# Changelog — business_info_display

## 2026-06-07 — Initial migration (VCITA2-13865)
- Migrated from `automation-js/features/tempo/business_info_page.feature`
  scenario `Update email in business info page`.
- Verifies the business info settings page shows the business name, owner email,
  and the Israel (972) country code.
- Added `get_business` + admin `update_business_country` helpers to account_api.
- Reads expected name/email from the API (auto_tester names accounts dynamically).
