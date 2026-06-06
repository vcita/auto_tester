# Apply service percentage coupon (created in UI) in CP checkout

A coupon scoped to the appointment_1 service is created in the Settings/Coupons UI, then a
client closes the whole outstanding balance in the client portal with it.

## Prerequisites (subcategory _setup)
- Logged in to the isolated account.
- 20% tax "TS" + two taxed "suggest to pay" ($100) services + mock gateway (see _setup).

## Steps
1. Create a client and book two PAST appointments (appointment_1, appointment_2) via API.
2. In Settings → Coupons, create a **10%** coupon **on the "appointment_1" service**, and
   read the generated coupon code from the post-save dialog.
3. Open the client portal as the client; go to the Payments list and click **Checkout** to
   close the whole balance (both appointments).
4. In the checkout dialog, apply the coupon by code, then pay via the mock gateway.
5. Verify the payment-success page shows **Payment confirmed**, "A confirmation email is on
   its way to your inbox", and **Amount received: $228.00** (appt_1 $108 + appt_2 $120).
