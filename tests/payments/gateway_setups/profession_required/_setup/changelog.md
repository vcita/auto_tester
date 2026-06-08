# Changelog: Wizard - profession required (setup)

## 2026-06-08 — Created (VCITA2-13903)
- Migrated the legacy no-business_category Platform-business create onto the runner's
  isolated account: `enable_wizard_flags` before login, no business_category so the
  preliminary profession step starts empty.
