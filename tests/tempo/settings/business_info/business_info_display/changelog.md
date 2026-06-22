# Changelog — business_info_display

## 2026-06-07 — Initial migration (VCITA2-13865)
- Migrated from `automation-js/features/tempo/business_info_page.feature`
  scenario `Update email in business info page`.
- Verifies the business info settings page shows the business name, owner email,
  and the Israel (972) country code.
- Added `get_business` + admin `update_business_country` helpers to account_api.
- Reads expected name/email from the API (auto_tester names accounts dynamically).

## 2026-06-07 — Wait audit + country read-back + iframe readiness
- `page.goto` lowered 15s -> 5s (`PAGE_TIMEOUT`); `domcontentloaded` fires fast.
- Added an explicit Angular iframe (`iframe[title="angularjs"]`) readiness wait before
  reaching into the frame, bounded at 10s (`IFRAME_TIMEOUT`) as a documented cross-iframe
  exception, so the field reads never race the iframe boot.
- Settings `_setup` now reads the country back (`wait_for_business_country`) after
  `update_business_country` and before login: the country write is eventually consistent,
  so the read-back guarantees the business-info page never renders a stale country (the
  reliability the legacy account-created-with-country setup got for free).
- script.md timing wording corrected: the 0.2s sleep is the poll interval inside the
  bounded <=5s `_input_value_when_ready` poll, not a blind fixed sleep.
