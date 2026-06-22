# Changelog — Sales Widget Full Display

## 2026-06-06 — Initial migration (VCITA2-13854)
- Migrated from `automation-js/features/salsa/sales_widget.feature` scenario
  "Sales widget - full display".
- Seeds revenue (paid invoice $10), one pending estimate, and three overdue
  appointment fees ($10/$40/$30 at 2/9/35 days past) via API, then asserts the
  widget's total revenue, pending estimates, overdue payments + age breakdowns,
  and the click-through navigation to Payments Received / Estimates / Billing.
- `assert_widget_values` uses a bounded (40s) reload-and-poll for the backend
  rollup (documented eventual-consistency budget).

## 2026-06-07 — Restore data-qa redirect selectors + wait audit
- `assert_redirect` now asserts the back-office page header by its `data-qa` id
  (`[data-qa="Payments Received"]` / `[data-qa='Estimates']` /
  `[data-qa="Billing & Invoicing"]`), mirroring the legacy
  getPaymentsReceived/Estimates/BillingAndInvoicing header checks and matching the
  documented selector policy. (It previously used a role-based heading match.)
- `NAV_TIMEOUT` halved 20000→10000 (documented dashboard/iframe render-readiness
  budget); element interactions stay at the 5s `STATE_TIMEOUT`. The revenue/overdue
  rollup keeps its bounded 40s eventual-consistency reload-poll.
