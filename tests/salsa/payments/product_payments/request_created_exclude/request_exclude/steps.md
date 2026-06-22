# Product payment request created (tax exclude)

Migrated from products.feature scenario 2.

## Steps

1. Assign **payable_item1** to **first last** via the client card, applying both
   taxes (13% + 13.13%).
2. Assert the product payment request is **DUE $12.61** for **first last**
   (price + tax, exclusive mode: 10 x (1 + 0.13 + 0.1313) = 12.61).
