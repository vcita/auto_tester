# Script: Product payment request created (tax exclude)

Source: products.feature scenario 2 (VCITA2-13858).

## Preconditions (setup)
- Isolated account, point_of_sale denied, default tax mode "exclude".
- Client "first last"; $10 product "payable_item1"; taxes 13% + 13.13%.

## Actions & assertions
1. `assign_product_ui("payable_item1", taxes=[13%, 13.13%])` -> assign through the
   client card Payments tab + AddProductDialog tax picker.
2. `assert_product_request_via_orders` -> DUE, $12.61, payable_item1, first last.
