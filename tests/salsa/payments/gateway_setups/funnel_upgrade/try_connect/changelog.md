# Changelog: Wizard - funnel v1 upgrade

## 2026-06-08 — Created (VCITA2-13903)
- Migrated legacy "user with payment funnel version one required to upgrade to connect to
  payment gateway". Opens the wizard, walks the connect-gateway path, and asserts the
  upgrade dialog appears on a funnel-v1 account.
- The funnel-v1 + legal_services flow surfaces a "Just one more thing" MCC clarification
  ("...Bankruptcy law related services" -> "Yes, these apply") between currency and
  connect-to-providers; `try_connect_gateway` clicks through up to `MAX_INTERSTITIALS=3`
  such interstitials (distinct wizard steps, not retries of one action) before reaching the
  third-party gateways link.

## Wait audit (pre-PR)
- `WIZARD_LOAD_TIMEOUT=20s` (payment_wizard_ui): justified — the onboarding wizard mounts
  through a 3-level iframe (POV -> Angular -> vue_wizard_iframe); element interactions stay
  capped at 5s.
- Upgrade-dialog assertion matches legacy (`#app` wizard root present); no weaker than legacy.
