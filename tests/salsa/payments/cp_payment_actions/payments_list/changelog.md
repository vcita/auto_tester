# Changelog — CP Payment Actions / payments_list

## Creation (VCITA2-14227)

Migrated `automation-js/features/salsa/cp/payment-actions.feature`
(Scenario: "Client portals payments list: client opens list with multiple requests") into
`tests/salsa/payments/cp_payment_actions/payments_list`.

- API setup: invoice ("product_item200" $20 + tax1 10% -> $22.00, #0000001), product
  "product2" $10, package "package1" ($150 specific, the setup service, total_bookings 2);
  assign product + package to the setup client; record a $100 partial payment on the package
  in the back office (leaves "Out of $150.00", list shows package $50.00).
- CP: open the payments list, assert 3 rows (product2 $10.00 Product, invoice #0000001
  $22.00 Invoice, package1 $50.00 Package), pay the package1 item via the mock gateway,
  assert the list then shows 2 rows (package1 gone).

## Reuse
- `account_api.create_package_via_api`, `assign_package_to_client`.
- `invoices.invoice_billing_api.create_invoice_via_api`.
- `product_payments.product_payments_api.create_product_via_api`, `assign_product_via_api`
  (the product_payments client store is pointed at the setup client so one client owns all
  three requests).
- `cp_payment_actions_helpers`: `record_package_payment` (BO TakePaymentDialog),
  `open_payments_list`, `assert_rows`, `pay_one_item` (CP list + mock popup, built on
  `coupons_checkout_cp`).
- `cp_payment_actions_api`: `make_invoice_items`, `invoice_due_date`,
  `get_client_package_id` (GET /platform/v1/clients/{id}/payment/client_packages).

## Math
Invoice item $20 + 10% tax = $22.00. Package $150 total - $100 recorded = $50.00 due
("Out of $150.00"). Product $10.00.

## Selector notes / waits
CP list rows/title/price/sub-title/comment/checkbox are legacy CSS (no data-qa). Take-payment
uses data-qa (take_payment, take-payment-confirmation); the money input is the custom Angular
control (mock layer + money_amount), payment method the md-select. Element waits ≤5s; bounded
re-check on the async-propagating list; CP nav + mock popup justified budget. No fixed sleeps
for actions (one minimal bounded poll for list propagation, documented).
