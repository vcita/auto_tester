# Cancel and refund paid product

Migrated from products.feature scenario 7.

## Steps

1. Record a **$5** payment for **payable_item1**.
2. Cancel the **payable_item1** payment request **with a refund**.
3. Assert the product payment request is **CANCELLED $10.00** for **first last**.
4. Assert Payments Received contains the **Payment for payable_item1** (refunded)
   for **first last**.
