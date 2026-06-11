# Setup: Product Request Created Exclude

## Steps

1. Deny the **point_of_sale** feature flag.
2. Log in to the isolated account.
3. Via API, create the client **first last** and a **$10** payable product
   **payable_item1** (Background).
4. Via API, create two taxes: **13%** and **13.13%** (default tax mode is
   "exclude").
