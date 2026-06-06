# Apply cart fixed-amount coupon in CP checkout

A client applies an entire-cart fixed-amount coupon while paying a single past meeting in
the client portal.

## Prerequisites (subcategory _setup)
- Logged in to the isolated account.
- 20% tax "TS" + two taxed "suggest to pay" ($100) services + mock gateway (see _setup).

## Steps
1. Create a client and book two PAST appointments (appointment_1, appointment_2) via API.
2. Create a $30 entire-cart coupon via API.
3. Open the client portal as the client; go to Bookings → Past → open "appointment_1".
4. Click the meeting's **Pay** action.
5. In the checkout dialog, apply the coupon by code, then proceed to payment and pay via the mock gateway.
6. Verify the payment-success page shows **Payment confirmed**, "A confirmation email is on its way to your inbox", and **Amount received: $84.00** (($100−$30) +20% tax).
