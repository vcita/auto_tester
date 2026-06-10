# Changelog — Upgrade Long Country

## 2026-06-11 — Initial migration (VCITA2-14028)
- Migrated automation-js `upgrade_page.feature` scenario 2 (long country name).
- Account: isolated Trial account (`package_subscription_id: 28`) with
  `country_name: "Bolivia, Plurinational State of"`. The `hide_register_wizard`
  feature flag is part of the runner's default automation flags, matching the
  legacy Platform-API create that set it explicitly.
  - Legacy created the business via Platform API (directory default package); we
    start Trial so the upgrade path is reproducible and equivalent. The scenario's
    distinguishing factor — the long country name — is preserved.
- UI flow + Recurly handling identical to upgrade_in_frontage (shared
  `upgrade_helpers.py`); card last name = "long country".
- Assertion: success-page package text == "vcita Platinum Single (Annual)" (matches
  the legacy scenario, which asserts only the package on the success page).

### Pre-PR Wait Audit (VCITA2-14028)
- Shares `upgrade_helpers.py` with upgrade_in_frontage, so the same bounded-poll
  justifications apply: get-it click loop 30s (nested-iframe re-render + 3rd-party
  tab open), hosted-field mount ≤12s, submit success poll ≤8s/attempt (≤2 retries),
  in-page token guard 10s. All are external Recurly/billing async, not flaky-selector
  masks; per-element waits ≤5s. No `data-qa` on plan cards or the 3rd-party Recurly
  page — legacy stable CSS selectors documented as the fallback.
- Stability re-confirmed after the final hardening: **10/10** focused stress
  (`settings/upgrade_page/upgrade_long_country`, integration, headless).
