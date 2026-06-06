# Pay for product (partial then full)

Migrated from products.feature scenario 4 "paying for product".

## Steps

1. Record a **$2** payment for **payable_item1**.
2. Assert the product payment request is **DUE $8.00 (out of $10.00)** for
   **first last**.
3. Assert **payable_item1** is listed in Billing & Invoicing (orders).
4. Assert Payments Received has one **Payment for payable_item1** for **first**.
5. Record an **$8** payment for **payable_item1**.
6. Assert the product payment request is **PAID $10.00** for **first last**.
7. Assert Payments Received has two **Payment for payable_item1** rows.
