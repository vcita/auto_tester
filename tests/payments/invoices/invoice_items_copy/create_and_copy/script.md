# Script — Create With Items And Copy Invoice

Helpers: `tests/payments/invoices/invoice_billing_ui.py` (UI) +
`tests/sales/estimates/estimates_helpers.py` (shared itemizable wizard).

## Flow
1. `create_and_send_invoice(page, context, name="product_invoice",
   client_name="first last", billing_address="blablablabla", new_items=[...])`
   - Opens Billing & Invoicing → New → Invoice (`billing_scope`/`wizard_scope` reused).
   - Selects client `first last`.
   - Adds two custom items via `add_custom_item` (name/price/description/tax/save_item).
     - `product`: save_item=True, tax = the seeded 13% tax (`[data-qa="tax-{name}-13"]`).
     - `product1`: save_item=False, no tax.
   - Sets the From billing address (best-effort, not asserted — matches legacy).
   - Issues via the wizard primary action `[data-qa="itemizable-dialog-main"]`
     (legacy "sends" → ISSUED). Handles the first-invoice numbering dialog if shown.
2. `assert_invoice_page(... title="product_invoice", number=1, state="ISSUED",
   amount="$66.95", client="first last")` — resolves the invoice id via
   `GET /platform/v1/invoices`, opens `/app/invoices/{id}`, polls body text.
3. `search_orders(["product_invoice #0000001"])` — loads `/app/payments/orders`,
   reads `f-ellipsis-tooltip.payment-title` rows, asserts exact ordered equality.
4. `create_and_send_invoice(... name="new_invoice",
   existing_items=[invoice_service_name, "product"])` — reuses the seeded service
   and the saved `product` item via `add_existing_item`.
5. `search_orders(["new_invoice #0000002", "product_invoice #0000001"])`.
6. `copy_invoice(page, "first last")` — opens the newest order, opens the invoice
   more-actions menu (`f-entity-actions .actions ... button`), clicks "Copy invoice",
   selects `first last`, issues the copied invoice.
7. `search_orders(["new_invoice #0000003", "new_invoice #0000002",
   "product_invoice #0000001"])`.

## Selectors / waits
- Wizard fields are POV `data-qa` (`itemizable-details-header`, `item-name`,
  `price`, `display-product-checkbox`, `tax-{name}-{rate}`, `itemizable-dialog-main`).
- Orders rows: `f-ellipsis-tooltip.payment-title` (legacy `paymentRow`).
- All waits are explicit condition waits / bounded polls (UI 5s, nav 20s, state 15s);
  no fixed sleeps beyond bounded poll intervals.
- Invoice numbering is deterministic on the fresh isolated account (#1, #2, copy #3).
