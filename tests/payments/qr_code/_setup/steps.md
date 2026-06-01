# Setup: QR Code Payment

Prepares the isolated account so the Pay-with-QR flow can run, mirroring the legacy
`qr-code-payment.feature` Background plus its mock-gateway precondition.

## Steps

1. **Enable `client_portal_checkout_v2`** on the account (before login) so the POS
   exposes the Pay-with-QR checkout action and the link checkout works.
2. **Log in** to the isolated account in the browser.
3. **Create a client** `first last` via the account API.
4. **Create a service** (`service-pay-<ts>`, appointment, "display a fee", $100) via the
   account API.
5. **Connect the mock payment gateway** (a connected gateway is required before the POS
   can take an online payment).

## Result

The account is logged in with a mock gateway connected, a client, and a $100 "display a
fee" service ready to sell from the POS.
