# Invoice With Late Fee

Migrated from automation-js `features/steps/invoices.feature` scenario
"create invoice with late fee".

Preconditions (from `_setup`): logged in on a fresh isolated US account with the
`first last` client, the paid "display a fee" service ($100), a 13% tax, and late
fees enabled (10% after 5 days).

Steps:
1. Create an invoice `new_invoice` for `first last` via API: billing address,
   the $100 service item, due on the 10th of next month, with late fee enabled.
2. Verify the invoice page shows `new_invoice #0000001`, client `first last`,
   state `ISSUED`, amount `$100.00`, and the "Subject to late fees" caption.
3. Verify a jobber execution `add_invoice_late_fee` exists with status `pending`,
   scheduled for the 15th of next month (due date + 5 days).
4. Trigger the `add_invoice_late_fee` jobber execution via API.
5. Verify the invoice page now shows `new_invoice #0000001`, `first last`, `ISSUED`,
   amount `$110.00` (the 10% late fee applied), still "Subject to late fees".
