# Payment confirmation emails via Point of Sale

Migrated from `payments-emails.feature` scenario 4 "payments confirmation emails via
Point of Sale".

## Steps

1. Use POS "record-payment" for the existing payment request of appointment **api1**
   ("service").
   - The client receives a **"Payment Confirmation"** email.
2. Record a payment for the client **first last** from POS, adding all the client's
   open requests.
   - The client receives a **second** "Payment Confirmation" email.

## Note

The legacy step text searches the client as "client last"; this migration selects
the client by the seeded full name "first last" (the account's only client), which
is deterministic. The asserted behavior (confirmation email per recorded payment)
is identical.
