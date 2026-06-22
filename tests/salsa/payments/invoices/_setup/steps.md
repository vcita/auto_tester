# Setup: Invoices (lifecycle chain)

Be logged in to an isolated account with the invoice prerequisites created via API.
Reuses the payments-domain setup so the create -> edit -> send -> cancel -> view
chain has the same required-payment service and invoice-picker client it expects.

## Steps

1. Log in to the isolated account (username/password from the account profile).
2. Create the invoice-picker client via API.
3. Create the required-payment invoice service via API.
