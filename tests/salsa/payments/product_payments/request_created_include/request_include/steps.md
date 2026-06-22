# Product payment request created (tax include)

Migrated from products.feature scenario 3.

## Steps

1. Assign **payable_item1** to **first last** via the client card, applying both
   taxes (13% + 13.13%).
2. Assert the product payment request is **DUE $10.00** for **first last** (tax
   included in the price, inclusive mode).
