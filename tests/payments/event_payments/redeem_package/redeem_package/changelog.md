# Changelog: Redeem event payment request with package

## 2026-06-06 — Initial migration (VCITA2-13856)
- Migrated event-payments.feature scenario 5 "Redeem event's payment request with
  package".
- Isolated subcategory `redeem_package`.
- Adds `create_event_package` / `assign_package_to_client` / `seed_event_package_redeem`
  API helpers and the `redeem_with_package` UI helper
  (`button[data-qa='redeem_package']`); verifies the request becomes PAID $0.00.
