# Pay for an invoiced product

Migrated from products.feature scenario 5.

## Steps

1. Create an invoice **product_invoice** (billing address blablablabla) from the
   **payable_item1** product payment request.
2. Pay the invoice **product_invoice #0000001** in full (**$10**).
3. Assert the product payment request is **PAID $10.00** for **first last**.
4. Assert Payments Received contains **Payment for product_invoice #0000001** for
   **first**.
