# Changelog - Tips Disabled Without Gateway

## 2026-05-30 - Created (migration)
- Migrated from automation-js `features/salsa/payments-settings/tips_settings.feature` scenario 1.
- Isolated account; `_setup` enables `rollout.payments.tips_settings`, denies
  `rollout.payments.gateway_platform`, then logs in.
- Test opens `/app/settings/payments?tab=tips` and asserts the disabled state via the
  `tips-tab-no-gateway-alert` data-qa selector (legacy parity).

## 2026-05-30 - Stability: reload poll for flag-propagation lag
- Stress run surfaced a cold-first-load race (1/10): the `gateway_platform` deny + cache reset
  occasionally had not propagated to the POV checkout-enabled read, so the tab briefly showed
  `enabled`. Added a reload loop (4 attempts, 3s backoff) so the assertion converges on the denied
  `disabled` state, mirroring the edit_persist reload pattern. Re-validated 10/10 stable.
