# Setup: Packaged Service Appointment

Prepares a fresh isolated account for the "Schedule appointment with packaged
service" scenario.

## Steps

1. Log in to the isolated account.
2. Via API, create the client **first last**.
3. Via API, create a **display a fee** service named **service** priced **$100**.
4. Via API, schedule two appointments for **first last** on **service**
   (**meeting1**, **meeting2**).
5. Via API, create a **2-credit $150** package offering **service** and assign
   it to **first last**.
