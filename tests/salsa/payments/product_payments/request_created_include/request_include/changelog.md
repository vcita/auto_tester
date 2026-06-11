# Changelog: Product payment request created (tax include)

## 2026-06-06 - Initial migration (VCITA2-13858)
- Migrated from products.feature scenario 3 "payments request created for product
  in mode include".
- Background (client + $10 product) and the two taxes are API-seeded;
  point_of_sale is denied; tax mode is set to "include".
- Assigns the product with both taxes through the client card Payments tab +
  AddProductDialog (the in-scope UI action), then asserts the product payment
  request is DUE $10.00 (tax included in price) on the Product Order page.
