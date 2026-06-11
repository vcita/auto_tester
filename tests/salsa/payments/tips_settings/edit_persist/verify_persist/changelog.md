# Changelog - Tips Edit Persist

## 2026-05-30 - Created (migration)
- Migrated from automation-js `features/salsa/payments-settings/tips_settings.feature` scenario 2.
- Isolated account; `_setup` enables `rollout.payments.tips_settings`, logs in, and connects the
  mock payment gateway via the providers UI.
- Test sets tips `55,66,77` via API, reloads the tips tab, asserts enabled state and preview amounts
  `$55.00/$66.00/$77.00` (legacy parity with parseTipsAmounts/formatPrice).

### Implementation notes (deviations from the legacy step, kept faithful to intent)
- Endpoint: legacy `PUT /v2/settings {tips:[...]}` returns 200 on meet2know but silently drops the
  `tips` field (GET shows `tips=None`). The tips tab reads/writes `payment_settings.tips` via
  `paymentSettingsService` (`POST /platform/v1/payment/settings`), so tips are set through that
  authoritative route and persistence is confirmed with an independent GET poll.
- Stability: the gateway-connect save in setup can land a late async write that resets
  `payment_settings.tips`, intermittently showing the default 10/15/20 preview. The verify step
  re-posts the tips and reloads with a short backoff until the saved values render. Confirmed
  10/10 (100%) over a stress run after this change.
