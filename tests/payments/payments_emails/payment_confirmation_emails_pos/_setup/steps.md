# Setup: Payment Confirmation Emails (POS)

Prepares a fresh isolated account (point_of_sale enabled by default) for scenario 4.

## Steps

1. Log in to the isolated account.
2. Via API, create the client **first last**.
3. Via API, create a **require to pay** service named **service** priced **$100**.
4. Via API, schedule an appointment **api1** for **first last** on **service**.
5. Via API, create a **$10** product **product21** and assign it to the client
   (the open request recorded via POS for the client).

No payment gateway is connected (matching the legacy scenario): the POS flow only
records offline Cash payments, which do not require a connected gateway.
