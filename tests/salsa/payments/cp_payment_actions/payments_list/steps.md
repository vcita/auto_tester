# payments_list — CP payments list with multiple requests

Migrates `automation-js/features/salsa/cp/payment-actions.feature`
(Scenario: "Client portals payments list: client opens list with multiple requests").

## API setup (per test, on the shared isolated account)
1. **Invoice** via API (`invoice_billing_api.create_invoice_via_api`) for the setup client:
   one item titled "product_item200", price 20, with tax "tax1" 10% -> displays **$22.00**.
   First invoice on a fresh account -> number **#0000001**.
2. **Product** "product2" price 10 via API (`product_payments_api.create_product_via_api`).
3. **Package** "package1" via API (`account_api.create_package_via_api`): specific, the setup
   service, total_bookings 2, price 150.
4. **Assign** product2 to the client (`product_payments_api.assign_product_via_api`).
5. **Assign** package1 to the client (`account_api.assign_package_to_client`, price 150).
6. **Record $100** on the package in the back office: resolve clientPackageID
   (`cp_payment_actions_api.get_client_package_id`), open `/app/client-package/{id}`,
   `[data-qa='take_payment']` -> Record section -> `input[name='money_amount']`=100 ->
   `md-select[name='payment_method']`=Cash -> `[data-qa='take-payment-confirmation']`.
   Leaves "Out of $150.00"; the CP list shows the package at **$50.00**.

## CP assertions + action
7. Open the CP payments list (open portal with the client token, payments menu). Assert it
   shows **3 rows** (order-sensitive):
   - product2 — $10.00 — Product
   - invoice #0000001 — $22.00 — Invoice
   - package1 — $50.00 — Package — comment "Out of $150.00"
8. Pay the **package1** item from the list (deselect select-all, check the package1 row,
   `.checkout-btn`, `[data-qa="perform-payment-action"]`, submit mock popup).
9. Assert the list now shows **2 rows** (package1 gone): product2 and invoice #0000001.

## Selectors / waits
CP list selectors are legacy CSS (no data-qa): rows `[paymentrequeststate]`, title
`[class=payment-title]`, price `[class*="price"]`, sub-title `.sub-title span.black-text`,
comment `[class*="comment"]`, row checkbox `.v-input--selection-controls__input`. Take-payment
data-qa first. Element waits ≤5s; bounded re-check on the async list; no fixed sleeps for actions.
