# Script — estimate_deposit_bo

Phase 2 (HOW). Flows live in `deposits_estimate_ui.py`, reusing the estimate dialog
helpers from estimates_helpers. Selectors confirmed against the legacy page objects
(`createDepositDialog.js`, `estimate.js`, `approveEstimateDialog.js`).

## Step 1 — Create + send estimate with deposit
```python
estimate_uid = create_estimate_with_deposit(
    page, context,
    title="bestimate", item_name="desired_item1", item_price="50",
    address="susa, persia", deposit_amount="10", can_client_pay=True,
)
```
open_new_estimate (estimates list -> New -> Estimate -> client picker) -> set title ->
add custom item $50 -> set billing address -> create-deposit: `create-deposit-button-text`
-> `deposit-amount-value`=10 -> `deposit-amount-types-item-fixed` -> `vc-footer-Done` ->
Send. Estimate uid resolved via API (no hardcoded `#0000001`).

## Step 2 — Verify SENT + deposit DUE $10.00
```python
assert_bo_estimate_deposit(page, context, estimate_uid, estimate_state="SENT", deposit_state="DUE", deposit_amount="$10.00")
```
Reads `deposit-item-text` (DUE) + `deposit-item-value` ($10.00); estimate state from the
back-office text.

## Step 3 — Approve & take payment (Cash)
```python
approve_and_take_payment(page, context, estimate_uid)
```
`approve_and_take_payment` -> `approve-checkbox` -> `deposit-take-payment` ->
`record_payment_button` -> Cash (`md-select[name='payment_method']`) ->
`take-payment-confirmation`.

## Step 4 — Verify APPROVED + deposit PAID $10.00
```python
assert_bo_estimate_deposit(page, context, estimate_uid, estimate_state="APPROVED", deposit_state="PAID", deposit_amount="$10.00")
```
Reads `deposit-item-text-paid` (PAID) + `deposit-item-value` ($10.00).
