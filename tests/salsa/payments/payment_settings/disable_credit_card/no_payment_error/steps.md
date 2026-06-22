# Online Payments - disable credit card payments in client portal

Migrated from `automation-js/features/salsa/payments_settings.feature` scenario 4
("Online Payments - disable credit card payments in client portal").

## Objective
Disable credit-card payments and verify a client cannot pay through the client portal
(no-payment error dialog).

## Preconditions (from _setup)
- Logged in to the isolated account.
- Client created via API (with portal token).

## Steps
1. Enter the payment settings page and assert the provider banner is displayed (before a
   provider is connected).
2. Connect the mock payment gateway (providers UI).
3. Disable credit-card payments via the payment settings API (`allow_credit_card=false`).
4. As the client, open the public make-payment form, attempt to pay, and verify the
   no-payment error dialog displays.
