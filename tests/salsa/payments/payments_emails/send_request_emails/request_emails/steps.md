# Send payment request emails (non-POS)

Migrated from `payments-emails.feature` scenario 1 "Send payment request emails to
client" (@gate).

## Steps

1. Send the payment-request link for appointment **api1** to the client by email.
   - The client receives an email whose subject starts with **"New payment request
     from "** (the business name suffix is the isolated account's name).
2. Invoice the **api1** appointment (invoice name **new_invoice**, billing address
   **blablablabla**).
   - The client receives an email whose subject starts with **"New invoice from "**.
3. Send the payment-request link for the invoice to the client by email.
   - The client receives a **second** email starting with **"New payment request
     from "**.
