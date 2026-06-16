# Pay for event (partial then full)

Migrated from `event-payments.feature` scenario 2 "paying for event".

## Steps

1. Record a $2 payment against the attendee's event payment request.
   - The request becomes **DUE $8.00 (out of $10.00)** for "first last" on the event.
   - Payments Received, filtered by "first", shows one **Payment for <event>** row.
2. Record a $8 payment against the same request.
   - The request becomes **PAID $10.00**.
   - Payments Received, filtered by "first", shows two **Payment for <event>** rows.
3. The client's portal conversation includes the title
   **Thank you for paying: Payment for <event>**.
