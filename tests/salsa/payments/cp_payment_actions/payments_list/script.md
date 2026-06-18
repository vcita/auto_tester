# payments_list — Detailed script

Source: `tests/salsa/payments/cp_payment_actions/payments_list/steps.md`
Migrated from `automation-js/features/salsa/cp/payment-actions.feature` (Scenario 2).

## Preconditions (from _setup)
`context["cp_payment_actions"]["service"]` ($100 service), `["client"]` (id + portal_token).

## Steps
1. **Invoice** (`create_invoice_via_api`): `title="invoice"`, `client_id=<client.id>`,
   `address="persepolis, persia"`, `items=make_invoice_items(title="product_item200",
   price="20", description="short desc", taxes=[{name:"tax1", rate:"10"}])`,
   `due_date=invoice_due_date()`. -> #0000001, $22.00.
2. **Product** (`create_product_via_api`): name "product2", price 10. (Needs the seeded
   client cached under product_payments; `seed_client` is reused so assign_product works.)
3. **Package** (`create_package_via_api`): name "package1",
   `services=[{id, name, price:"100", currency:"USD"}]` (the setup service),
   `total_bookings=2`, `price="150"`.
4. **Assign product** (`assign_product_via_api(product_name="product2")`).
5. **Assign package** (`assign_package_to_client(client_id, package_id, price="150")`).
6. **Record $100** on the package: `client_package_id = get_client_package_id(context,
   client.id, "package1")`; `record_package_payment(page, context,
   client_package_id=..., amount="100")`.
7. **Open CP payments list** (`open_payments_list(page, context, portal_token)`).
8. **Assert 3 rows** (`assert_rows`):
   product2 $10.00 Product | invoice #0000001 $22.00 Invoice | package1 $50.00 Package
   (comment "Out of $150.00").
9. **Pay package1** (`pay_one_item(cp_page, cp_frame, "package1")`). Lands on the CP
   payment-success page.
10. **Re-open the list** (`goto_payments_list(cp_frame)`) and **assert 2 rows** (`assert_rows`):
    product2 $10.00 Product | invoice #0000001 $22.00 Invoice.

## Notes
- `seed_client` (product_payments_api) is reused so `assign_product_via_api` finds the
  client; it is called with the same setup client identity so a single client owns all three
  requests (legacy uses one client for the whole scenario).
- Package item price is the service price ($100); the package total price is $150 (legacy).
- Element waits ≤5s; CP nav + popup justified budget; bounded re-check on the async list.
