# Changelog - Matters Management Setup

## 2026-06-08 - Initial migration (VCITA2-13952)
- Created from legacy matters-management.feature Background.
- Logs in to the isolated account and creates two contacts ("matter client",
  "contact client") via `account_api.create_client` (POST /platform/v1/clients).
- Client creation kept as API (legacy Background was API; not a tested UI behavior).
