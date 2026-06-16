# Invoice In Tax Include Mode

Migrated from automation-js `features/steps/invoices.feature` scenario
"create invoice in mode include".

Preconditions (from `_setup`): logged in on a fresh isolated US account with the
`first last` client, the paid "display a fee" service, a 13% tax, and the account
tax mode set to `include`.

Steps:
1. Create and send a new invoice `product_invoice` to `first last` with a billing
   address and two new custom items:
   - `product` — "short desc", $15, saved, with the 13% tax.
   - `product1` — "long desc", $50, not saved, no tax.
2. Verify the invoice page shows `product_invoice #0000001`, client `first last`,
   state `ISSUED`, amount `$65.00` (tax is included in the item prices, so the total
   is 15 + 50 rather than 66.95).
