# Changelog — Orders Filter / filter_orders

## Creation (VCITA2-13852)

Migrated `automation-js/features/steps/orders.feature` ("filter orders") into
`tests/sales/orders_filter` as an isolated-account subcategory under `sales`.

- **_setup/test.py** (`setup_orders_filter`): isolated-account UI login + API
  creation of client "first last" and the paid service "service" ($100, "require
  to pay" -> charge_type `paid_force`). Fixed names are safe (fresh account) and
  keep the Orders list deterministic.
- **orders_filter_helpers.py**: `assert_orders_filtered` opens the Angular Orders
  page (`/app/payments/orders`, scoped via `estimates_helpers.billing_scope`),
  applies the `[name="type_filter"]` md-select (clear-all -> enable requested ->
  Escape, mirroring legacy `filterByPaymentType`), waits for the list loader to
  clear, and asserts `f-ellipsis-tooltip.payment-title` texts equal the expected
  list **in order** (legacy `should.eql`).
- **filter_orders/test.py** (`test_filter_orders`): creates the booking, package,
  and assignment via API (preserving the legacy API steps) and asserts the four
  type-filter result sets: bookings -> ['service']; packages ->
  ['test_package - Package purchased']; bookings+packages ->
  ['test_package - Package purchased', 'service']; invoices -> [].
- **tests/account_api.py**: added reusable `create_package_via_api` and
  `assign_package_to_client` (POST /platform/v1/payment/packages and
  /client_packages), backward-compatible additions mirroring the legacy
  api/packages helpers.

## Selector notes (data-qa to add in product code)

The Angular Orders type filter has no data-qa. Reused stable legacy selectors:
`[name="type_filter"]`, the type options `[name="bookings|invoices|packages|products"]`,
the list loader `.f-list-loader [aria-hidden="false"]`, and the result rows
`f-ellipsis-tooltip.payment-title`. data-qa should be added to these in the app.

## Waits / eventual consistency

Element/interaction waits capped at 5s; the only longer wait is NAV_TIMEOUT for the
Angular Orders page navigation/render readiness (justified, not an element wait).
Orders indexing of API-created bookings/packages can lag (legacy retried ~30×1s),
so `assert_orders_filtered` reloads at most twice and polls the filtered list up to
5s per attempt (~15s bounded budget). No fixed sleeps beyond short inter-poll/reload
backoffs.

## Validation (integration, headless)

- py_compile: OK.
- `main.py list --category sales`: `sales/orders_filter` registered.
- 3 focused runs: PASSED (30.3s / 28.3s / 27.5s).
- stress_test --iterations 3: PASSED (3/3, 100%).
- Pre-PR wait audit: PASSED (element waits ≤5s; NAV_TIMEOUT justified; reloads ≤2).
