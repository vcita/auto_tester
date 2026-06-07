# Playwright HOW-TO — CP follow-up tip on a paid meeting

All UI runs in the Vue client portal inside `#cp_iframe` on the public livesite, in a
fresh browser context opened with the client's portal token (`open_portal`). The tip is
completed in the external mock-gateway popup. Implemented by
`tips_checkout_cp.add_meeting_followup_tip`.

## Flow
- `open_portal(page, context, portal_token)` (fresh CP context).
- Bookings menu `[data-qa='client-area-menu-bookings']` → Past tab `[data-qa="tab-selector-past"]`.
- Open the meeting: `.booking-title:has-text("require")`.
- Add a tip: `[data-qa="addTip"]` (only shown on a paid, completed meeting with CP tips on).
- Checkout dialog `.checkout-dialog`; the follow-up tip uses the **legacy Tips.vue** bar
  (NOT the new `checkout-tips__segment`): pick the percent tip by
  `xpath=//div[@class="tip-first-line" and contains(.,"66%")]`.
- Pay: `[data-qa="perform-payment-action"]` → mock popup `button[type=submit]`.

## Assertion
- Success page `[data-qa='payment-success-page']`:
  - `span.briliant` == `Thank you for tipping!`
  - first `span.paymet-text` == `Amount received: $66.00`

## Selector notes (data-qa gaps)
- The follow-up tip percent buttons (`.tip-first-line` / `.tip-button` in legacy Tips.vue)
  have no product data-qa; the stable legacy XPath is reused and documented. `addTip`,
  the bookings menu, the past tab, and the success page all expose data-qa.
