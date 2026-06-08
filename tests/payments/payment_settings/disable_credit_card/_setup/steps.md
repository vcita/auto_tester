# Disable Credit Card — Setup

## What it does
1. Log in to the isolated account (UI).
2. Create the client (with portal token) used to open the make-payment form.

## Notes
- The mock gateway is connected in the test (after the provider banner is asserted),
  because the banner only shows before a provider is connected (legacy order).
