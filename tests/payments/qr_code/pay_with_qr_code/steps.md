# Pay With QR Code

A business generates a Pay-with-QR payment link from the POS checkout, the client pays
it from a separate tab, the POS QR dialog confirms the payment, and the resulting
payment is verified in the back office.

## Steps

1. Open the POS for the client (Quick Actions → Take payment → pick `first last`).
2. Add the `service-pay-<ts>` service to the sale, open the checkout actions, choose
   **Pay with QR code**, and grab the payment link the QR dialog exposes.
3. In a second tab, open the payment link, proceed to payment, and pay with the mock
   gateway until the success page appears.
4. Back on the POS QR dialog, confirm it shows **payment received** (realtime) and close it.
5. In the back office (Payments Received), open the payment and verify it shows:
   - name **"Payment for Sale #1 - service-pay-<ts>"**
   - amount **$100.00**
   - type **Credit Card (Online)**
   - item **service-pay-<ts>**

## Expected Result

The QR payment completes end to end: the POS dialog confirms success and the back-office
payment record matches the sale (name, amount, online card type, and item).
