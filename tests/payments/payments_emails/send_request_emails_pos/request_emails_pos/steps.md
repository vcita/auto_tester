# Send payment request emails via Point of Sale

Migrated from `payments-emails.feature` scenario 2 "Send payment request emails to
client via Point of Sale".

## Steps

1. Use POS "send-link" for the existing payment request of appointment **api1**
   ("service").
   - The client receives an email starting with **"New payment request from "**.
2. Schedule a second appointment **api2** via API, then invoice it (invoice name
   **new_invoice**, billing **blablablabla**).
   - The client receives an email starting with **"New invoice from "**.
3. Send the payment-request link for the invoice to the client by email.
   - The client receives a **second** email starting with **"New payment request
     from "**.

## Note

`api2` uses its own require-to-pay service ("service2") so the Orders-routed invoice
targets it unambiguously. The legacy used the same service name for both
appointments; this is a workflow-only difference (both are require-to-pay; the
asserted invoice email is identical), with no scope loss.
