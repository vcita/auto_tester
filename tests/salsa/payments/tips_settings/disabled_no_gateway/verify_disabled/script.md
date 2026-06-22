# Tips Disabled Without Gateway - Script

## Locators
- Tips tab: `[data-qa="tips-tab"]`
- No-gateway alert (disabled signal): `[data-qa="tips-tab-no-gateway-alert"]`
- Tip amount input (enabled signal): `[data-qa="tips-tab-amount-1"]`

## Actions
1. `open_tips_settings(page, context)`:
   - `page.goto("{base_url}/app/settings/payments?tab=tips")`.
   - Wait for `[data-qa="tips-tab"]` visible (resolves across frames; POV is top-level).
2. `get_tips_status(scope)`:
   - Poll up to 5s: if `tips-tab-no-gateway-alert` visible -> `disabled`; if `tips-tab-amount-1`
     visible -> `enabled`.
3. Reload loop (up to 4 attempts, 3s backoff): re-open the tips tab and re-check status; return as
   soon as it is `disabled`. The `gateway_platform` deny + cache reset run in setup, but the POV
   checkout-enabled read can lag on a cold first load, so a backoff lets it converge.
4. Assert status == `disabled`.

## Notes
- The disabled state is driven by `isCheckoutEnabled` (no connected gateway), so the no-gateway
  alert is the authoritative disabled signal.
