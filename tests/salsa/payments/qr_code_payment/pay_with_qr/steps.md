# Pay with QR code

Migrated from `automation-js/features/salsa/qr-code-payment.feature` (scenario
"pay with QR code"), VCITA2-13850.

## Preconditions (setup)
- Isolated account with `client_portal_checkout_v2` enabled (before login).
- Logged in to the account (`point_of_sale` enabled by default).
- Client `first last` created via API.
- Paid service `service-pay+<ts>` (display a fee, $100, appointment) created via API.

## Steps
1. Configure the mock payment gateway in the back office.
2. From the POS, grab a QR-code payment link for client `first last` with the paid
   service item in the sale.
3. The client pays via the grabbed link in a separate browser tab through the mock
   gateway, and the mobile payment success page is shown.
4. The back-office QR-code dialog shows payment success; close it (Done).
5. The Payments Received payment page displays:
   - name: `Payment for Sale #1 - service-pay+<ts>`
   - amount: `$100.00`
   - type: `Credit Card (Online)`
   - items: `[service-pay+<ts>]`
