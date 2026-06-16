# Changelog: Product payment request created (tax exclude)

## 2026-06-06 - Initial migration (VCITA2-13858)
- Migrated from products.feature scenario 2 "payments request created for product".
- Background (client + $10 product) and the two taxes are API-seeded;
  point_of_sale is denied; default tax mode is "exclude".
- Assigns the product with both taxes through the client card Payments tab +
  AddProductDialog (the in-scope UI action), then asserts the product payment
  request is DUE $12.61 (10 x (1 + 0.13 + 0.1313)) on the Product Order page.
