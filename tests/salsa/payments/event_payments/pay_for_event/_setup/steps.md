# Setup: Pay for event

Prepares an isolated account for the "pay for event" scenario.

1. Deny the `point_of_sale` feature flag (so the payment request's "take payment"
   opens the legacy record-payment dialog rather than Point of Sale).
2. Log in to the isolated account.
3. Via API: create client "first last", create a "require to pay" $10 event
   service, schedule the event, and register the client as an attendee.
