# Setup: Convenience Fee Flat

## Objective
Provision an isolated account ready to demonstrate offset card fees at the
client-portal checkout.

## Steps
1. Enable the offset-fee feature flags on the account (before login).
2. Log in to the isolated account.
3. Create a paid ("suggest to pay") $100 appointment service via API.
4. Create a client via API and capture the client-portal JWT token.
5. Schedule a past appointment (10th of the previous month) for that service/client via API.
6. Connect the mock payment gateway (UI).
7. Enable credit-card + ACH bank payments via API so a second payment method exists.
8. Save a credit card on file for the client (UI, mock gateway).

## Expected Result
The account has a mock gateway connected, ACH enabled, a saved card on the
client, and a past appointment carrying a $100 payment request payable from the
client portal.

## Context Updates
- `offset_service`, `offset_service_name`
- `offset_client`, `created_client_name`
- `offset_booking_id`
