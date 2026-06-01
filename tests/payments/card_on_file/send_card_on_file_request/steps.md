# Send Card on File Request — Steps

Migrated from `automation-js/features/salsa/card-on-file.feature`
(scenario: *user sends request to add card on file*).

Precondition (from setup): an isolated account with a mock payment gateway
connected and a client (`first last`) created via API.

1. Send a card-on-file request to the client (open the client's Payments tab,
   open the add-payment-method dialog, choose "Request card on file", send it).
2. Verify the client card shows the pending request: `Card request sent on <today>`.
3. Verify the client receives the email with subject `Confirm your preferred payment method`.
