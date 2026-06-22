# Changelog — Scheduling With Taxes

## 2026-06-09 — Initial migration (VCITA2-14008, scenario 3/4)

Migrated `payment-setups.feature` scenario "Services and Scheduling with taxes".

**Built**
- `payment_setups_api.create_tax`: create a tax via `/business/payments/v1/taxes` with
  optional `default_for_categories`.
- `_setup/test.py`: create client + three taxes + API-only `suggest2pay` service, log in,
  connect the mock payment gateway.
- `payment_setups_ui.create_service_ui`: extended with a `taxes` argument — quick dialog
  "With fee" path + `_add_taxes` (Edit link → `md-select` tax picker → `tax-{name}-{rate}`).
- Extended `multistaff_helpers.schedule_appointment` price override with taxes
  (`_select_taxes`): conditional `edit-tax-link`, `tax-picker-button`, `VcCheckbox` DOM click.
- `test.py`: create the taxed UI services, assert the services-list tax text, schedule four
  appointments (one tax override), verify meeting prices + payment-request tax math, then flip
  `tax_mode` to include and verify the tax-inclusive amount.

**Scope/quality**
- Full legacy scope preserved: default-for-services tax, UI + API services, combined tax
  (10%+5%=15%), appointment tax override, DUE / NOT-YET-DUE payment requests with
  `$X ($Y + Tax)` math, and the tax_mode include flip with the prior request unchanged.

**Fixes during build (found via focused runs)**
- `_select_taxes` clicked `edit-tax-link` unconditionally; for a service whose picker is shown
  directly the link is absent → now clicked only when visible.
- The tax `VcCheckbox` is not actionable for a synthetic Playwright click (30s timeout); it is
  toggled via its own DOM `click` handler (mirrors the proven `product_payments` tax-picker).
- `Escape` closed the entire appointment dialog (first run's closed-dialog screenshot); the
  popover is now closed by clicking the picker field again.
- The 250ms appointments read-back poll tripped the per-business `APPOINTMENTS_LIMIT_EXCEEDED`
  (429) across five bookings; relaxed to 1.5s (still resolves the new id, ~6x fewer calls).

**Run evidence**
- 2026-06-09 focused run: PASSED (2/2), body ~85s (3 UI services + list asserts + 5 schedulings
  + meeting reads + payment-request asserts + tax_mode flip).
