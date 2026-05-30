# Back-office Partial Refund - Steps

## Objective
Record a custom-item payment via the Quick Actions legacy dialog, refund a partial amount, and verify the payment page.

## Preconditions
- Logged in to the isolated account with `point_of_sale` denied; client `Torry Deposi` exists; no payment gateway.

## Steps
1. Open Quick Actions and choose `Record payment`.
2. Select client `Torry Deposi`.
3. Record a custom-item Cash payment of `5` (item name `custom_item`).
4. Open the payment `Payment for custom_item` from Payments Received.
5. Issue a partial refund of `1`.
6. Verify the payment page shows name `Payment for custom_item`, amount `$5.00`, refund `-$1.00`.

## Expected Result
- Payment page displays the custom-item payment with a `-$1.00` partial refund.
