# Script: Create and search product

Source: products.feature scenario 1 (VCITA2-13858).

## Preconditions (setup)
- Isolated account; client "first last"; $10 product "payable_item1"; taxes 13% + 13.13%.

## Actions & assertions
1. `create_product_ui(name="product2", description=..., price="10", cost="5",
   sku="1234678", taxes=[13%])` -> Add product dialog.
2. `search_products_ui("product2", ["product2"])` -> found by name.
3. `search_products_ui("1234678", ["product2"])` -> found by SKU.
