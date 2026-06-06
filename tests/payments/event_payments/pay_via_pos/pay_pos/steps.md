# Pay for event via Point of Sale

Migrated from `event-payments.feature` scenario 2b "paying for event via Point of Sale".

## Steps

1. Record the attendee's event payment request through Point of Sale (the event
   item is pre-loaded; checkout -> Record payment -> Cash).
2. Orders, filtered by **PAID**, lists **Sale #1 - <event>**.
3. The Sale page shows **Sale #1 - <event>**, client **first last**, state
   **PAID**, amount **$10.00**.
4. Payments Received, filtered by "first", lists **Payment for Sale #1 - <event>**.
5. The client's portal conversation includes the title **Payment for <event>**.
