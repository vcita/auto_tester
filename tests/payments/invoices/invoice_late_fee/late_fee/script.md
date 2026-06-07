# Script — Invoice With Late Fee

Helpers: `tests/payments/invoices/invoice_billing_api.py` (API + jobber) +
`invoice_billing_ui.assert_invoice_page` (UI assertion).

## Flow
1. `create_invoice_via_api(title="new_invoice", client_id, address="blablablabla",
   items=[{title: service, amount: 100, quantity: 1}],
   due_date=next_month_day(10), enable_late_fee=True)` — legacy used API to create
   this invoice (the scenario tests the late-fee lifecycle, not the create wizard).
2. `assert_invoice_page(... title="new_invoice", number=1, state="ISSUED",
   amount="$100.00", late_fee="Subject to late fees")`.
3. `assert_jobber_execution(event_name="add_invoice_late_fee", status="pending",
   expected_date=next_month_day(15))` — `GET /business/jobber/executions/{pivot}`.
   We assert the event name, pending status, and the scheduled date (due + 5 days),
   rather than the exact business-timezone timestamp string (robust, same coverage).
4. `trigger_jobber_execution("add_invoice_late_fee")` — `POST .../{uid}/execute`.
5. `assert_invoice_page(... amount="$110.00", late_fee="Subject to late fees",
   force_reload=True)` — re-opens the invoice fresh so the updated total is read.

## Notes
- All waits are bounded condition polls (jobber poll 15s; UI 5s; nav 20s; state 15s).
- The invoice is API-created (matches legacy "user creates new invoice via API"); the
  user-visible state (ISSUED / late-fee caption / totals) is verified through the UI.
