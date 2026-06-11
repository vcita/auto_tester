# Changelog — cp_followup_tip / add_tip_in_cp

## Migration (VCITA2-13899)
Migrated from `automation-js/features/salsa/tips.feature`, scenario
"take followup tip in cp".

### Setup (API + minimal UI)
- `seed_cp_followup_tip_account`: tips flags, `tips` app (Admin auth), tip options
  `55/66/77` enabled for CP (POST `/platform/v1/payment/settings` + read-back), client
  `first last` (portal token kept), a require-to-pay `require` ($100) + suggest-to-pay
  `suggest` ($50) service, a past appointment for each, and a recorded $100 Cash payment
  for the `require` meeting so it is fully paid (the prerequisite for the CP "Add a tip"
  follow-up action).
- UI: BO login + connect mock payment gateway (`tips_settings/tips_gateway`).

### Test actions (UI under test)
- Client `first last` opens the CP, goes to Bookings → Past, opens the `require` meeting,
  clicks Add a tip, picks the `66%` follow-up tip, and pays via the mock-gateway popup.
- Asserts the CP payment success page: title `Thank you for tipping!` and
  `Amount received: $66.00`.

### New helper
- `tips_checkout_cp.add_meeting_followup_tip`: CP bookings → past → meeting → Add a tip →
  legacy Tips.vue percent bar → mock popup → success-page assertion.

### Selector considerations (data-qa gaps)
- The follow-up tip percent buttons use the legacy `Tips.vue` markup
  (`.tip-first-line` inside `.tip-button`) with **no product data-qa**; the stable legacy
  XPath `//div[@class="tip-first-line" and contains(.,"66%")]` is reused and documented.
  This differs from the new pay-link checkout tip bar (`checkout-tips__segment`) used in
  cp_paylink_tips. `addTip`, the bookings menu, the past tab, and the success page all
  expose data-qa. Suggest adding data-qa to the follow-up Tips.vue percent buttons.
