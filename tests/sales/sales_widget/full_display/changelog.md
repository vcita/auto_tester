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
