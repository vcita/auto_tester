# Changelog — set_terms

## 2026-06-07 — Initial migration (VCITA2-13901)
- Migrated payments_settings.feature scenario 2 (Terms and Policies).
- Sets terms text via the payment settings API and verifies both the API read-back and
  the terms-and-policies settings tab textarea display the text. Mock gateway connected
  in setup (legacy precondition).
