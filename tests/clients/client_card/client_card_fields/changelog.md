# Changelog: Client and contact custom card fields

## 2026-06-06 — Initial migration (VCITA2-13855)
- Migrated from `automation-js/features/steps/client-card.feature` (scenario
  "client card fields").
- Added `tests/clients/client_card` subcategory (isolated account) with `_setup`
  (login) and the `client_card_fields` test.
- Custom fields (client + contact) created via Client Card Settings UI; clients
  seeded via API; CRM filtering + filtered-client assertions reuse the
  `crm_filters` helpers.
- Preserved the legacy scope exactly, including that the post-rename re-search is
  omitted (SUPPORT-6006) — only the rename action is verified.
