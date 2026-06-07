# Sales Widget — Empty State (script)

Source scenario: `automation-js/features/salsa/sales_widget.feature` — "Sales widget - empty state - no payments set".

## Flow
1. `goto_new_dashboard` → `{base_url}/app/dashboard`.
2. `assert_empty_state` locates the loaded widget (`.sales-widget--loaded`, on the
   POV page or an embedded frame) and waits for the empty-state title
   (`.payment-widget-list__empty-state-title`), the empty list
   (`[data-qa='PaymentWidgetListEmptyState']`), and the CTA button
   (`... .VcEmptyStateButton`).
3. `open_payment_wizard` clicks the CTA and waits for the payment wizard root
   (`.wizard-content.payment-wizard-get-paid-online`) which renders inside a Vue
   iframe, so the helper scans `page.frames` for it.

## Selectors
- data-qa where available (`PaymentWidgetListEmptyState`, value tiles). The
  loaded-container / empty-title / wizard-root have no data-qa, so stable legacy
  CSS is reused (see `sales_widget_helpers.py` header). Suggested product change:
  add `data-qa` to `.sales-widget--loaded` and the payment-wizard root.

## Waits
- Element waits capped at 5s. Dashboard/iframe readiness uses NAV_TIMEOUT (20s),
  a render-readiness budget, not a fixed sleep.
