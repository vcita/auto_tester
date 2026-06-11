# Tips Edit Persist - Script

## Locators
- Tips tab: `[data-qa="tips-tab"]`
- Tip amount input (enabled signal): `[data-qa="tips-tab-amount-1"]`
- No-gateway alert (disabled signal): `[data-qa="tips-tab-no-gateway-alert"]`
- Preview amounts: `.tips-preview__tip-option-amount`

## Actions
1. `set_tips_via_api(context, [55, 66, 77])`:
   - POST `{api_base_url}/platform/v1/payment/settings` (Bearer auto_account token), body
     `{payment_settings:{tips:[{type:"percent",value:55},{...66},{...77}]}}`, confirmed by an
     independent GET poll. (Legacy used `PUT /v2/settings`, which no longer persists `tips`; the POV
     tips tab reads/writes `payment_settings.tips` via this payment-settings route.)
2. Reload loop (`clear_profile_cache` + `open_tips_settings`), re-posting tips on each retry:
   navigate to the tips tab (fresh load = the legacy refresh).
3. `get_tips_status(scope)` -> assert `enabled`.
4. `get_preview_amounts(scope, expected=...)` -> assert `["$55.00", "$66.00", "$77.00"]`.

## Notes
- The preview renders `$priceDisplay(tip.value, currency)`, so percent values 55/66/77 display as
  `$55.00/$66.00/$77.00` (this is the same value the legacy `formatPrice` produced).
- The setup gateway-connect save can land a late async write that resets `payment_settings.tips`;
  the verify step re-posts tips and reloads with a short backoff until the saved values render.
