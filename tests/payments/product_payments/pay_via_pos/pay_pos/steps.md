# Pay for product via Point of Sale

Migrated from products.feature scenario 4b.

## Steps

1. Record the **payable_item1** payment through **Point of Sale** (record-payment,
   Cash).
2. Assert the product payment request is **PAID $10.00** for **first last**.
3. Assert Payments Received contains **Payment for Sale #1 - payable_item1** for
   **first**.
