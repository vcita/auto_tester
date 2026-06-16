# Setup: Send Payment Request Emails

Prepares a fresh isolated account (point_of_sale denied) for scenario 1.

## Steps

1. Deny the **point_of_sale** feature flag (so take payment uses the legacy
   send-payment-link dialog, not Point of Sale).
2. Log in to the isolated account.
3. Via API, create the client **first last**.
4. Via API, create a **require to pay** service named **service** priced **$100**.
   (Require-to-pay rather than the legacy "suggest to pay" so the appointment payment
   request appears as a DUE order in Billing & Invoicing - the SPA entry point that
   mounts the POV invoice wizard. The emails under test are charge-type-independent,
   so no email-scope is lost; same pattern as appointment_payments/invoiced_appointment.)
5. Via API, schedule an appointment **api1** for **first last** on **service**.
6. Connect the mock payment gateway (so the payment-request channel is available).
