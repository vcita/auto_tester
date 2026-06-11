# Edit and cancel product's payment request

Migrated from products.feature scenario 6.

## Steps

1. Edit the **payable_item1** payment request amount to **$20**.
2. Assert the product payment request is **DUE $20.00** for **first last**.
3. Cancel the **payable_item1** payment request.
4. Assert the product payment request is **CANCELLED $20.00** for **first last**.
