# Setup: Cancel And Refund Product

## Steps

1. Deny the **point_of_sale** feature flag (so take payment uses the legacy
   record-payment dialog).
2. Log in to the isolated account.
3. Via API, create the client **first last** and a **$10** payable product
   **payable_item1** (Background).
4. Via API, assign **payable_item1** to **first last**.
