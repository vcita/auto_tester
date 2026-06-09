# Scheduling With Taxes — Script

Migrated from `payment-setups.feature` scenario "Services and Scheduling with taxes".

## Flow

1. **Setup (`_setup/test.py`)** — create the client + three taxes via API
   (`payment_setups_api.create_tax`): `default_tax` (10%, `default_for_categories=services`),
   `non_default_tax` (5%), `another_tax` (15%); create the API-only `suggest2pay` service
   ($50, `charge_type=paid`, **no** tax); log in; connect the mock payment gateway
   (`tips_gateway.connect_mock_gateway`) so appointments produce DUE / NOT-YET-DUE payment
   requests.

2. **Create three UI services** (`payment_setups_ui.create_service_ui`) — `require2pay`
   (require to pay, $100), `displayFree` (display free), `another require` (require to pay,
   $100, with the non_default 5% tax added in the quick dialog). The default-for-services 10%
   tax auto-applies to every UI service, so `another require` shows a combined 15%.

3. **Verify the services list** (`services_categories_helpers.assert_service_details`):
   `suggest2pay` → $50, no Tax; `require2pay` → $100 (+10% Tax); `displayFree` → Free;
   `another require` → $100 (+15% Tax).

4. **Schedule four appointments** (`multistaff_helpers.schedule_appointment`); `suggest2pay`
   overrides the tax to `another_tax` 15% via `price_override={"taxes": [...]}`.

5. **Verify meeting prices** (`read_meeting_price`): `displayFree` → Free; `require2pay` →
   `110.00 ($100.00 + Tax)`.

6. **Verify payment requests** (`appointment_payments_helpers.assert_appt_payment_request`,
   tax-exclusive mode): require2pay → DUE $110.00; suggest2pay → NOT YET DUE $57.50; another
   require → DUE $115.00 — each `$X ($Y + Tax)`.

7. **tax_mode include** (`invoice_billing_api.set_tax_mode`) — schedule another `require2pay`
   and verify the new request is tax-inclusive ($100.00) while the earlier require2pay request
   keeps its tax-exclusive amount ($110.00 ($100.00 + Tax)).

## Locator decisions

- **UI service tax** — quick service dialog "With fee" path; the `Edit` tax link
  (`a[ng-click='enableTaxFlow()']`) reveals the Angular `md-select` tax picker
  (`md-option[data-qa="tax-{name}-{rate}"]`).
- **Appointment tax override** — `FeeTypeGenerator.vue` price panel. The `Edit` link
  (`[data-qa='edit-tax-link']`) shows only in the summary view; it is clicked **only when
  present** to reveal the `TaxPicker`. The picker is opened via
  `[data-qa='tax-picker-button']`; each `[data-qa="tax-{name}-{rate}"]` `VcCheckbox` is
  toggled with a DOM `click` (the Vue overlay swallows Playwright's synthetic click) guarded by
  `is_checked()`. The popover is closed by **clicking the picker field again** — `Escape`
  closes the whole appointment dialog.
- **Payment requests** — reused `assert_appt_payment_request`; appointments are registered in
  the `appointment_payments` store by identifier so the shared reader can open them.

## Verified

- 2026-06-09: focused run PASSED (2/2), body ~85s.
- The appointments-list read-back poll was relaxed from 250ms to 1.5s: a tight loop across
  five bookings tripped the per-business `APPOINTMENTS_LIMIT_EXCEEDED` (429) quota.
