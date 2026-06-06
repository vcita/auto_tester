# Create ad-hoc sale - refund

Migrated from `automation-js/features/salsa/sales.feature` — scenario
"Create ad-hoc sale - refund".

## Preconditions (from _setup)
- Logged in to a fresh isolated account.
- Client "first last" created via API (so the sale is attributed to that client).

## Steps
1. Connect the mock payment gateway (back office) so the client can pay online.
2. As the client, open the client-portal public payment form for a `meeting`
   payment of `$20`.
3. Pay through the form via the mock gateway (fill email + first name, submit,
   confirm payment in the mock-gateway popup).
4. Verify the payment success page shows **Payment confirmed** and
   **Amount received: $20.00**.
5. Verify Orders filtered by **PAID** lists **Sale #1 - meeting**.
6. Verify Payments Received search for "first" lists **Payment for Sale #1 - meeting**.
7. Verify the sale page shows name **Sale #1 - meeting**, client **first last**,
   state **PAID**, amount **$20.00** (USD).
8. Refund the payment **Payment for Sale #1 - meeting** (full refund).
9. Verify Orders filtered by **CANCELLED** lists **Sale #1 - meeting** (and the
   sale page now shows state **CANCELLED**).

## Expected result
The ad-hoc payment creates a paid sale, the payment and sale are searchable and
correctly stated, and a full refund moves the sale to CANCELLED.
