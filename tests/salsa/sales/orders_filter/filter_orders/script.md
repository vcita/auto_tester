# Script — Filter orders by payable type

Source scenario: `automation-js/features/steps/orders.feature` ("filter orders").
Implementation: `test.py` + `tests/sales/orders_filter/orders_filter_helpers.py`
+ package helpers in `tests/account_api.py`.

## API setup inside the test (preserved from legacy API steps)
- `create_appointment_via_api(context, service, client)` →
  POST `/business/scheduling/v1/bookings` {business_id, staff_id, future start_time,
  service_id, client_id}.
- `create_package_via_api(context, "test_package", services=[service], total_bookings=2,
  price="150")` → POST `/platform/v1/payment/packages`
  {items:[{services:[{name,price,currency,id}], total_bookings:2}], products:[],
  discount_unit:"p", online_payment_enabled:true, expiration:"3", expiration_unit:"m",
  name, description:"", price:"150", id:null, currency:"USD", use_platform_api:true}.
- `assign_package_to_client(context, client_id, package_id, "150")` →
  POST `/platform/v1/payment/client_packages` {client_id, package_id, price:"150",
  valid_from=yesterday, valid_until=+3mo-1d, tax_uids:null, use_platform_api:true}.

## UI assertions (the behavior under test)
Navigate to `{base_url}/app/payments/orders`, scope into `iframe[title="angularjs"]`
via `estimates_helpers.billing_scope`.

`assert_orders_filtered(page, context, types, expected)`:
1. Reload Orders, wait for the type-filter md-select to be visible.
2. Open `[name="type_filter"]`, deselect every payable option
   (`[name="bookings|invoices|packages|products"]`) that is `selected`, then enable
   the requested ones; press Escape to close (mirrors legacy `filterByPaymentType` +
   `sendEscOnElement`).
3. Wait for `.f-list-loader [aria-hidden="false"]` to clear, then read
   `f-ellipsis-tooltip.payment-title` texts and compare to `expected` **in order**
   (legacy `res.should.eql(results)`).

Expected lists:
- bookings → `["service"]`
- packages → `["test_package - Package purchased"]`
- bookings + packages → `["test_package - Package purchased", "service"]` (package first)
- invoices → `[]`

## Selectors & waits
- No data-qa on the Angular Orders type filter/options/loader/rows — reuse the stable
  legacy CSS; data-qa should be added in product code (`type_filter`, the type options,
  the list loader, and the payment-title rows).
- Element/interaction waits ≤ 5s. The single longer wait is NAV_TIMEOUT (Angular Orders
  page navigation/render readiness after `page.goto`), which is justified app-navigation
  readiness, not an element-interaction wait. Orders indexing of API-created entities can
  lag, so the assertion reloads at most twice and polls the filtered list up to 5s each
  attempt (bounded eventual-consistency budget, ~15s total; not a fixed sleep).
