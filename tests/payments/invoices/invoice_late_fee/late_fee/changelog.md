# Changelog — Invoice With Late Fee

## 2026-06-07 — Initial migration (VCITA2-13900)
- Migrated from automation-js `features/steps/invoices.feature` scenario
  "create invoice with late fee".
- Isolated US account; late fees enabled in `_setup`.
- API: `create_invoice_via_api` (legacy created this invoice via API),
  `assert_jobber_execution` / `trigger_jobber_execution` against
  `/business/jobber/executions/...`.
- UI assertions via `assert_invoice_page`: ISSUED $100.00 + "Subject to late fees",
  then $110.00 after triggering the late-fee job.
- Jobber assertion verifies event name, pending status, and scheduled date (due + 5
  days = 15th of next month) rather than the exact business-timezone timestamp.
