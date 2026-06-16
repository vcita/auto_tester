# Changelog — update_currency

## 2026-06-07 — Initial migration (VCITA2-13901)
- Migrated payments_settings.feature scenario 1 (Currency - update default currency).
- Verifies USD default, switches to EUR via the payment settings API
  (save + update_default_currency), and asserts the read-back and a newly scheduled
  meeting reflect EUR. Stronger than the legacy (which left the currency check a no-op).
