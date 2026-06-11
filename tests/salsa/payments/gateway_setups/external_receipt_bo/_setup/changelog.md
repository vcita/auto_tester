# Changelog: External receipt - back office (setup)

## 2026-06-08 — Created (VCITA2-13903)
- Migrated the legacy Background: deny `point_of_sale`, login, create `simon bolivar`,
  assign `mockreceipts`. Reuses `gateway_setups_account.prepare_receipt_account`,
  `account_api.create_client/deny_features`, and `tips_checkout_api.assign_app`.
