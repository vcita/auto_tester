# Sales Widget — Full Display (script)

Source scenario: `automation-js/features/salsa/sales_widget.feature` — "Sales widget - full display".

## API setup (prerequisites, not the tested behavior)
- `create_client` (platform/v1/clients).
- `create_fee_service` x3 — `create_service_via_api(charge_type="paid_non_secured", price=...)` for $10/$40/$30 "display a fee" services.
- `schedule_past_appointment` x3 — POST `/business/scheduling/v1/bookings` with `start_time` 2/9/35 days in the past, so each fee is overdue in the 1-7 / 8-30 / 31+ day bucket.
- `create_product` ($80) + `create_estimate_via_api` (signature required, send_email) + `create_deposit_request` → one pending estimate.
- `create_invoice` + `record_payment` ($10 Cash, subject Invoice) → $10 revenue.

## UI behavior (the tested part)
- `assert_widget_values` reloads `/app/dashboard`, locates the loaded widget, and
  reads `PaymentWidget-TotalRevenue|PendingEstimates|OverduePayments` value tiles
  plus the `.overdue-breakdown` rows (normalizing ` | ` to `,`). It polls up to
  AGG_TIMEOUT (40s) because the revenue/overdue rollup lags the API writes — a
  bounded eventual-consistency budget, not a fixed sleep.
- `assert_redirect` clicks each value tile and waits for the POV back-office page
  header (`[data-qa="Payments Received"]`, `[data-qa='Estimates']`,
  `[data-qa="Billing & Invoicing"]`).

## Selectors
- All widget values and page headers use data-qa. Only the loaded-container uses
  legacy CSS (no data-qa). Suggested product change: add `data-qa` to
  `.sales-widget--loaded`.
