# Script: Edit and cancel product's payment request

Source: products.feature scenario 6 (VCITA2-13858).

## Preconditions (setup)
- Isolated account; client "first last"; $10 product "payable_item1" assigned.

## Actions & assertions
1. `edit_product_amount("20")` -> set the request amount to $20.
2. `assert_product_payment_request` -> DUE, $20.00, payable_item1, first last.
3. `cancel_product_request()` -> waive the request (no refund).
4. `assert_product_payment_request` -> CANCELLED, $20.00, payable_item1, first last.
