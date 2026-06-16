# Setup: QR Code Payment (isolated account)

Mirrors the legacy `qr-code-payment.feature` Background.

## What it does
1. Enable the `client_portal_checkout_v2` feature flag on the isolated account
   **before** logging in, so the back-office session exposes the POS "Pay with QR
   code" checkout action (feature flags are read into the session at login).
2. Log in to the isolated account.
3. Create the client `first last` via API (email `test+<ts>@vmeetme.com`).
4. Create the paid service `service-pay+<ts>` via API: appointment, USD, price 100,
   charge type `paid_non_secured` (legacy "display a fee").

## Saved to context
- `qr_client_name` = "first last"
- `qr_client_email`
- `qr_client_first_name` = "first"
- `qr_service_name` = "service-pay+<ts>"

## Notes
- `point_of_sale` is enabled by default on the isolated account (the POS Quick
  Action relies on this, same as the deposits POS scenario).
