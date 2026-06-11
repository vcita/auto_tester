# Setup: Payment Confirmation Emails

Prepares a fresh isolated account (point_of_sale denied) for scenario 3.

## Steps

1. Deny the **point_of_sale** feature flag (record-payment dialog, not POS).
2. Log in to the isolated account.
3. Via API, create the client **first last**.
4. Via API, create a **suggest to pay** service named **service** priced **$100**.
5. Via API, schedule an appointment **api1** for **first last** on **service**.
6. Via API, create a **$10** product **product21** and assign it to the client (so
   the client has an open balance to close).
