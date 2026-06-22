# Setup: Custom Fee Service Appointment

Prepares a fresh isolated account for the "paying for custom fee service
appointment" scenario.

## Steps

1. Log in to the isolated account (point_of_sale enabled by default).
2. Via API, create the client **first last**.
3. Via API, create a **display for a fee** (price varies) service named
   **service** (no fixed price).
4. Via API, schedule an appointment for **first last** on **service**.
5. Via API, create a **13%** tax named **TStax**.
