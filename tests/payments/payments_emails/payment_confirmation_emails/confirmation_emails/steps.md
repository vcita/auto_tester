# Payment confirmation emails (non-POS)

Migrated from `payments-emails.feature` scenario 3 "payments confirmation emails"
(@gate).

## Steps

1. Pay **$30** for appointment **api1** (record a Cash payment, send receipt).
   - The client receives a **"Payment Confirmation"** email.
2. Close the client's payments balance via **record** / **ACH** with send-receipt.
   - The client receives a **second** "Payment Confirmation" email.
