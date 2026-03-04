# Record Full Payment

## Objective
Record a full payment for a service via the Checkout page and verify the payment record.

## Prerequisites
- User is logged in
- A client exists
- No payment gateway connected

## Steps
1. Navigate to the Checkout page (`app/pos`) via the sidebar (Sales -> Checkout)
2. Add a Custom Item with a name and price (e.g. ₪50)
3. Select a client from the client selector
4. Press the "Checkout" button
5. Select "Record payment" from the payment options menu
6. Select "Cash" as the payment method (full amount is pre-filled)
7. Click the "Record" button
8. Verify automatic redirection to the Payment page and check the payment details (status "Paid", method "Cash")

## Expected Result
- Payment is recorded successfully
- User is redirected to the Payment page automatically
- Payment record is visible with the correct amount and method

## Context Updates
- Save `recorded_payment_id`, `recorded_payment_amount`, `recorded_payment_method`
