# Setup: Send Payment Request Emails (POS)

Prepares a fresh isolated account (point_of_sale enabled by default) for scenario 2.

## Steps

1. Log in to the isolated account.
2. Via API, create the client **first last**.
3. Via API, create a **require to pay** service named **service** priced **$100**.
4. Via API, schedule an appointment **api1** for **first last** on **service**.
5. Connect the mock payment gateway (POS checkout requires a connected gateway).
