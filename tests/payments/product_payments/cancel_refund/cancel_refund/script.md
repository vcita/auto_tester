# Script: Cancel and refund paid product

Source: products.feature scenario 7 (VCITA2-13858).

## Preconditions (setup)
- Isolated account, point_of_sale denied; client "first last"; $10 product
  "payable_item1" assigned.

## Actions & assertions
1. `pay_for_product("5")` -> record a $5 Cash payment.
2. `cancel_product_request(refund=True)` -> waive the request and issue a refund.
3. `assert_product_payment_request` -> CANCELLED, $10.00, payable_item1, first last.
4. `search_payments("first", "Payment for payable_item1", 1)` -> the refunded
   payment is present in Payments Received.
