# Changelog: crm_mobile/_setup

## 2026-06-20 - Initial migration (VCITA2-14251)
- Isolated-account setup mirroring the legacy crm-mobile.feature Background.
- Logs in as owner (fn_login), then seeds the 10 `crm_mobile_clients.csv` clients via API
  (`seed_csv_clients` -> `account_api.create_client`, `POST /platform/v1/clients`).
- Emails are made unique per run via a `seq` time suffix (legacy `[seq]` token).
- CSV tags (rows 2 & 3 -> tag4) are NOT seeded: the only tag-using legacy step is
  commented out / out of scope.
- `crm_mobile_seq` saved to context.
