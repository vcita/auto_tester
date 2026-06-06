# Cancel and refund paid event

Migrated from `event-payments.feature` scenario 3 "Cancel and refund paid event".

## Steps

1. Record a full $10 payment against the attendee's event payment request.
2. Cancel the whole event, choosing the **refund** option.
3. Payments Received, filtered by "first", lists **Payment for <event>**
   (the refunded payment).
