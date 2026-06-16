# Changelog: Wizard - populated profession (setup)

## 2026-06-08 — Created (VCITA2-13903)
- Migrated the legacy Platform-business create (business_category + wizard flags) onto the
  runner's isolated account: `enable_wizard_flags` + `set_business_category("legal_services")`
  before login. Avoids creating a fresh directory while preserving the wizard entitlements.
