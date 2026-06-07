# Create With Items And Copy Invoice

Migrated from automation-js `features/steps/invoices.feature`
scenario "create invoice with new and existing items, and copy invoice".

Preconditions (from `_setup`, all via API on a fresh isolated US account):
- Logged in.
- Client `first last` exists.
- Paid "display a fee" service ($100) exists.
- A 13% tax exists.

Steps:
1. Create and send a new invoice `product_invoice` to `first last` with a billing
   address and two new custom items:
   - `product` — "short desc", $15, saved as a reusable item, with the 13% tax.
   - `product1` — "long desc", $50, not saved, no tax.
2. Verify the invoice page shows `product_invoice #0000001`, client `first last`,
   state `ISSUED`, amount `$66.95` (15 + 13% tax = 16.95, plus 50).
3. Verify the orders list shows exactly `product_invoice #0000001`.
4. Create and send a second invoice `new_invoice` to `first last` reusing the existing
   `service` and the saved `product` items.
5. Verify the orders list shows exactly `new_invoice #0000002`, `product_invoice #0000001`.
6. Copy the most recent invoice for `first last` and send it.
7. Verify the orders list shows exactly `new_invoice #0000003`, `new_invoice #0000002`,
   `product_invoice #0000001`.
