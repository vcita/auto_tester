# Set Up Invoice Late Fee (UI + Client Portal) - Steps

## Objective
End-to-end parity with the legacy "Set up invoice late fee": configure amount-based late
fees through the settings UI, create and send an invoice with late fee enabled, verify the
business-side invoice, and verify the client-portal invoice shows the late-fee caption.

## Prerequisites (from _setup)
- Logged in to the isolated US account.
- Client `first last` exists (with portal token); a `display a fee` service ($100) exists.

## Steps
1. Set late-fee settings in the Billing & Invoicing settings UI: enabled, type=amount,
   amount=10, after 5 days; save. Confirm it persisted as enabled.
2. Create and send a new invoice (`new_invoice`) for `first last`, billing address
   `blablablabla`, item = the service, with the late-fee toggle enabled.
3. Verify the business-side invoice page: `new_invoice #0000001`, client `first last`,
   state ISSUED, amount $100.00, late fee "Subject to late fees".
4. As the client, open the client portal and open the pending payment request
   `new_invoice #0000001`.
5. Verify the client-portal invoice page: name `new_invoice #0000001`, client `first last`,
   price $100.00, late fee "Late fees".

## Expected Result
- Business invoice shows ISSUED / $100.00 / "Subject to late fees".
- Client-portal invoice shows the invoice, $100.00, and "Late fees".
