# Changelog: Wizard - funnel v1 upgrade (setup)

## 2026-06-08 — Created (VCITA2-13903)
- Migrated the legacy funnel-v1 Platform-business create onto the runner's isolated
  account: `enable_wizard_flags(funnel_v1=True)` + `set_business_category("legal_services")`
  before login.
