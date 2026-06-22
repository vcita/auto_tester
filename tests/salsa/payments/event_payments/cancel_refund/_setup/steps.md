# Setup: Cancel and refund paid event

Prepares an isolated account for the cancel-and-refund scenario.

1. Deny the `point_of_sale` feature flag (record-payment via the legacy dialog).
2. Log in to the isolated account.
3. Via API: create client "first last", create a "require to pay" $10 event
   service, schedule the event, and register the client as an attendee.
