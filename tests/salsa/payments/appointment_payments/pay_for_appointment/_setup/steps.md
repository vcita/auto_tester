# Setup: Pay For Appointment

Prepares a fresh isolated account (point_of_sale denied) for the "paying for
appointment" scenario.

## Steps

1. Deny the **point_of_sale** feature flag (so take payment uses the legacy
   record-payment dialog).
2. Log in to the isolated account.
3. Via API, create the client **first last**.
4. Via API, create a **display a fee** service named **service** priced **$100**.
5. Via API, schedule an appointment for **first last** on **service**.
