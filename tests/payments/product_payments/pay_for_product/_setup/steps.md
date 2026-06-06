# Setup: Pay For Product

Prepares a fresh isolated account (point_of_sale denied) for the "paying for
product" scenario.

## Steps

1. Deny the **point_of_sale** feature flag (so take payment uses the legacy
   record-payment dialog).
2. Log in to the isolated account.
3. Via API, create the client **first last** and a **$10** payable product
   **payable_item1** (Background).
4. Via API, assign **payable_item1** to **first last** (creates the DUE product
   order under test).
