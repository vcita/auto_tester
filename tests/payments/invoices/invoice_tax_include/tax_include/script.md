# Script — Invoice In Tax Include Mode

Helpers: `tests/payments/invoices/invoice_billing_ui.py`.

## Flow
1. `create_and_send_invoice(page, context, name="product_invoice",
   client_name="first last", billing_address="blablablabla", new_items=[
     {product, $15, save_item, tax 13%}, {product1, $50}])`
   - Same itemizable wizard as scenario 1; issues via `[data-qa="itemizable-dialog-main"]`.
2. `assert_invoice_page(... title="product_invoice", number=1, state="ISSUED",
   amount="$65.00", client="first last")`.

## Notes
- Tax mode `include` is set in `_setup` before the wizard loads, so the wizard computes
  the tax-inclusive total ($65.00 vs $66.95 in add mode).
- Waits are explicit condition waits / bounded polls (UI 5s, nav 20s, state 15s).
