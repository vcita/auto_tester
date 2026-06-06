# Script: Pay for product (partial then full)

Source: products.feature scenario 4 "paying for product" (VCITA2-13858).

## Preconditions (setup)
- Isolated account, point_of_sale denied.
- Client "first last"; $10 payable product "payable_item1" assigned (DUE order).

## Actions & assertions
1. `pay_for_product("2")` -> record a $2 Cash payment (legacy record dialog).
2. `assert_product_payment_request` -> DUE, $8.00 (out of $10.00), payable_item1,
   first last.
3. `assert_order_listed("payable_item1")` -> order present in Billing & Invoicing.
4. `search_payments("first", "Payment for payable_item1", 1)`.
5. `pay_for_product("8")` -> record an $8 Cash payment.
6. `assert_product_payment_request` -> PAID, $10.00, payable_item1, first last.
7. `search_payments("first", "Payment for payable_item1", 2)`.
