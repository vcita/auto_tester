# Apply cart percentage coupon in CP checkout

A client applies an entire-cart percentage coupon while paying a single past meeting in
the client portal.

## Prerequisites (subcategory _setup)
- Logged in to the isolated account.
- 20% tax "TS" created via API.
- Two taxed "suggest to pay" ($100) services "appointment_1"/"appointment_2" created via API.
- Mock payment gateway connected.

## Steps
1. Create a client and book two PAST appointments (appointment_1, appointment_2) via API.
2. Create a 10% entire-cart coupon via API.
3. Open the client portal as the client; go to Bookings → Past → open "appointment_1".
4. Click the meeting's **Pay** action.
5. In the checkout dialog, apply the coupon by code, then proceed to payment and pay via the mock gateway.
6. Verify the payment-success page shows **Payment confirmed**, "A confirmation email is on its way to your inbox", and **Amount received: $108.00** ($100 −10% +20% tax).
