# Script: Pay for an invoiced product

Source: products.feature scenario 5 (VCITA2-13858).

## Preconditions (setup)
- Isolated account; client "first last"; $10 product "payable_item1" assigned
  (DUE order).

## Actions & assertions
1. `invoice_product("product_invoice", "blablablabla")` -> create an invoice from
   the product order (POV-routed via Billing & Invoicing).
2. `pay_for_invoice("product_invoice #0000001", "10")` -> record a Cash payment.
3. `assert_product_payment_request` -> PAID, $10.00, payable_item1, first last.
4. `search_payments("first", "Payment for product_invoice #0000001", 1)`.

Note: the legacy `type | invoice` column is documented but not asserted (legacy
`parseProductOrderParams` ignores it); the PAID state + amount are the checks.
