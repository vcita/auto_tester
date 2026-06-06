# Setup: Invoiced Appointment

Prepares a fresh isolated account for the "Paying for invoiced appointment"
scenario.

## Steps

1. Log in to the isolated account.
2. Via API, create the client **first last**.
3. Via API, create a **require to pay** service named **service** priced **$100**.
   (Require-to-pay so the appointment payment request appears as a DUE order in
   Billing & Invoicing, the SPA entry point that mounts the POV invoice wizard;
   the invoice->PAID behavior under test is identical to display-a-fee.)
4. Via API, schedule an appointment for **first last** on **service**.
