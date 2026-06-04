# Script — invoice_deposit_pos

Phase 2 (HOW). Flows live in `deposits_pos_ui.py` (POS record) and `deposits_invoice_ui.py`
(invoice + deposit). Selectors confirmed against the legacy POS page object (`Pos.js`,
`dialogs/createCustomItemDialog.js`, `takePaymentDialog.js`) and the invoice dialog
(`invoiceAndEstimateDialogs.js`).

## Steps 1/2 — Record two POS custom-item sales
```python
record_pos_custom_payment(page, context, item_name="deposit_item", price="5")
record_pos_custom_payment(page, context, item_name="regular_item1", price="3")
```
Quick Actions -> `VcLargeQuickAction-point_of_sale` -> client picker -> POS. Create item:
`pos-add-custom-item` -> `item-name` + `custom-item-price` -> `vc-footer-Add`. Checkout:
`checkout-actions-activator` -> `checkout-action-record` -> take-payment dialog
(`md-dialog.take-payment-wrapper`) -> Cash (`md-select[name='payment_method']`) ->
`take-payment-confirmation`. Each call creates one Sale (#1, #2). Dialog close = readiness.

## Step 3 — Create + send invoice with assigned deposit
```python
create_invoice_with_deposit(
    page, context,
    title="deposit_invoice", item_name="big invoice", item_price="50",
    deposit_payment_title="Payment for Sale #1 - deposit_item",
)
```
Same itemizable-dialog flow as scenario 1; the POS sale payment is titled
"Payment for Sale #1 - deposit_item".

## Verification — invoice summary
```python
assert_invoice_deposit(page, context, amount="$45.00 (out of $50.00)", deposit_sum="$5.00", state="ISSUED")
```
Latest invoice resolved via API (no hardcoded `#0000001`); read amount/state/deposit-row.
