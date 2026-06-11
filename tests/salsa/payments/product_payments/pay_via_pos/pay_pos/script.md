# Script: Pay for product via Point of Sale

Source: products.feature scenario 4b (VCITA2-13858).

## Preconditions (setup)
- Isolated account, point_of_sale enabled; client "first last"; $10 product
  "payable_item1" assigned.

## Actions & assertions
1. `record_product_via_pos()` -> take payment opens POS; checkout -> Record
   payment -> Cash -> confirm.
2. `assert_product_payment_request` -> PAID, $10.00, payable_item1, first last.
3. `search_payments("first", "Payment for Sale #1 - payable_item1", 1)`.
