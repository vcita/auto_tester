# Changelog — cp_paylink_tips / pay_and_close_balance

## Migration (VCITA2-13899)
Migrated from `automation-js/features/salsa/tips.feature`, scenario
"take payment with tips in cp via pay link".

### Setup (API + minimal UI)
- `seed_cp_tip_account`: tips feature flags, `tips` app (Admin auth), tip options
  `55/66/77` enabled for CP (POST `/platform/v1/payment/settings` + read-back),
  suggest-to-pay `service` ($100), client `first last` (portal token kept), and a past
  appointment for `first last` so it has a payable CP balance.
- UI: BO login + connect mock payment gateway (required for the CP checkout to accept
  payment) — reuses `tips_settings/tips_gateway.connect_mock_gateway`.

### Test actions (UI under test)
- Part A: new client `steve` pays the `service` via the public make-payment pay link,
  adds a `55%` tip in the Vue checkout dialog, and pays via the mock-gateway popup.
- Part B: existing client `first last` closes their CP balance from the payments list
  with a `5` custom tip, paying via the mock-gateway popup.
- Both payments are asserted on the back-office Payments Received detail page
  (client/name/amount/items/tip) via `tips_checkout_bo.assert_payment_page_with_tip`.

### New helper
- `tips_checkout_cp.py`: CP pay-link + close-balance tip flows, reusing the
  `coupons_checkout_cp` CP-session / `#cp_iframe` / mock-gateway-popup pattern.

### Selector considerations (data-qa gaps)
- The CP checkout tip bar (`button.checkout-tips__segment`, custom-tip modal input
  `.v-text-field__slot input`, apply `button.action-dialog__apply-btn`) has no product
  data-qa; stable legacy CSS from `clientPortalDialogs.js` is reused and documented.
- The public make-payment identity inputs have no data-qa; selected by adjacent label
  (`xpath=//label[contains(.,"Email")]/../input`). Suggest adding data-qa to the CP
  checkout tip controls and public-form identity inputs.
