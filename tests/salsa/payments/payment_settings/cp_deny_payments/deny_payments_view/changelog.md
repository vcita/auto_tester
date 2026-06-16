# Changelog — deny_payments_view

## 2026-06-07 — Initial migration (VCITA2-13901)
- Migrated payments_settings.feature scenario 3 (CP deny payments view).
- Confirms the Payments action is present by default, denies view payments via the API,
  and verifies the action is hidden. Reuses open_portal for the CP session.
