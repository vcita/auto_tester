# Paying for an invoiced event

Migrated from `event-payments.feature` scenario 4 "Paying for and invoiced event".

## Steps

1. Create an invoice from the attendee's event payment request (invoice name
   "event_invoice", a billing address).
2. Pay the resulting invoice **event_invoice #0000001** for **$10**.
3. The invoice page shows state **PAID**, amount **$10.00**, client **first last**,
   item **<event>**, invoice **event_invoice #0000001**.
4. Payments Received, filtered by "first", lists **Payment for event_invoice #0000001**.
