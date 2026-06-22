# Setup: Pay Appointment Via POS

Prepares a fresh isolated account (point_of_sale enabled) for the "paying for
appointment via Point of Sale" scenario.

## Steps

1. Log in to the isolated account (point_of_sale enabled by default).
2. Via API, create the client **first last**.
3. Via API, create a **require to pay** service named **service-rtp** priced **$100**.
4. Via API, schedule an appointment for **first last** on **service-rtp**.
