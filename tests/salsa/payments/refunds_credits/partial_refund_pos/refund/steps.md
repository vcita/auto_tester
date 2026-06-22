# POS Partial Refund - Steps

## Objective
Record a custom-item payment via Point of Sale, refund a partial amount, and verify the payment page.

## Preconditions
- Logged in to the isolated account; client `Torry Deposi` exists; Point of Sale enabled; no payment gateway.

## Steps
1. Open Checkout (Point of Sale).
2. Add a custom item named `custom_item` priced `5`.
3. Select client `Torry Deposi`.
4. Checkout and record a Cash payment (lands on the payment page).
5. Issue a partial refund of `1`.
6. Verify the payment page shows name `Payment for Sale #1 - custom_item`, amount `$5.00`, refund `-$1.00`.

## Expected Result
- Payment page displays the custom-item payment with a `-$1.00` partial refund.
