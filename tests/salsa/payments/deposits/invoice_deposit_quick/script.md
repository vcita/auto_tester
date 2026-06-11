# Script — invoice_deposit_quick

Phase 2 (HOW). Flows live in `deposits_invoice_ui.py` and `deposits_api.py`; this test
orchestrates them. Selectors confirmed against the legacy page objects
(`oldPaymentsDialogs.js`, `invoiceAndEstimateDialogs.js`, `assignDepositDialog.js`,
`invoice.js`) and the auto_tester Quick-Actions/picker pattern (scheduled_payments_ui).

## Step 1 — Deny point_of_sale, re-login
```python
deny_features(context, "point_of_sale")
relogin(page, context)
```
Quick Actions exposes `item-record_payment` only without POS (legacy denies POS then
re-logs in via API). Feature flags are read at login, so a soft reload keeps the old
entitlements — `relogin` clears cookies/storage and runs `fn_login` for a fresh session.

## Step 2/3 — Record two custom payments (Quick Actions)
```python
record_custom_payment(page, context, item_name="deposit_item", amount="5")
record_custom_payment(page, context, item_name="regular_item1", amount="3")
```
Quick Actions -> `item-record_payment` -> client picker -> title autocomplete
"Custom Item" -> `input[name='custom_item_name']` -> `.amount-field input` -> Cash ->
confirm (`charge-payment`/`save-payment`). Dialog close is the readiness signal.

## Step 4 — Create + send invoice with assigned deposit
```python
create_invoice_with_deposit(
    page, context,
    title="deposit_invoice", item_name="big invoice", item_price="50",
    deposit_payment_title="Payment for deposit_item",
)
```
Quick Actions -> `item-invoice` -> picker -> wizard (`#vue_wizard_iframe`): set title,
add custom item $50 (reused `add_custom_item`), `assign-deposit-button-text` ->
`[data-qa="Payment for deposit_item"]` -> `vc-footer-Done`, send (`itemizable-dialog-main`).

## Verification — invoice summary
```python
assert_invoice_deposit(page, context, amount="$45.00 (out of $50.00)", deposit_sum="$5.00", state="ISSUED")
```
Resolve the client's latest invoice via API (no hardcoded `#0000001`), open it, and read
`div.summary-header h2 span` (amount), `[data-qa="payment_status_state"]` (state),
`.deposit-row > .invoice-right-side` (deposit).
