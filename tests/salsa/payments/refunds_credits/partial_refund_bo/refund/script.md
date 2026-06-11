# Back-office Partial Refund - Detailed Script

## Actions
### Step 1: Open Quick Actions -> Record payment
- Click `[data-qa="vcMenu-QuickAction"]`, then `[data-qa="item-record_payment"]` (present because `point_of_sale` is denied).

### Step 2: Select client
- In the `iframe[title="angularjs"]` dialog pick `Torry Deposi`.

### Step 3: Record custom-item payment
- Title field `input[name="paymentService"]` -> select `Custom Item`.
- `input[name='custom_item_name']` = `custom_item`; amount `.amount-field input` = `5`.
- Open record section (`[data-qa="record_payment_button"]` if present); `md-select[name='payment_method']` = `Cash`.
- Confirm (`save-payment` / `charge-payment` / `take-payment-confirmation`).

### Step 4: Open payment
- Navigate to Payments Received, search by client name, open `Payment for custom_item`.

### Step 5-6: Partial refund and verify
- `partial_refund_current_payment(page, "1")`, then `assert_payment_page(page, "Payment for custom_item", "$5.00", "-$1.00")`.

## Selector Notes
- Legacy dialog selectors mirrored from `OldPaymentsDialogs` / `TakePaymentDialog` in automation-js, scoped to the angularjs iframe.
