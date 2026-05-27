# EU Strict Invoice Refund Credit Notes - Steps

## Objective
Verify that EU strict invoices created under an Italy account produce credit notes after full and partial refunds.

## Prerequisites
- The `eu_strict_invoices` subcategory setup has logged in to an isolated Italy account.
- A client named `first last` exists.
- A paid service priced at `100` exists.

## Steps
1. Create and send the first invoice for `first last` with billing address `Rome, Italy`.
2. Verify the first invoice is issued for `$100.00`.
3. Search Billing & Invoicing orders for the first invoice.
4. Record a full cash payment for the first invoice.
5. Verify the first invoice is paid for `$100.00`.
6. Fully refund the payment for the first invoice.
7. Verify the first invoice is paid, credited, and has `$0.00` balance.
8. Verify the first invoice has one credit note and the credit-note PDF opens.
9. Create and send a second invoice for the same client and service.
10. Record a full cash payment for the second invoice.
11. Partially refund the second invoice payment for `$60.00`.
12. Partially refund the second invoice payment for `$40.00`.
13. Verify the second invoice is paid, credited, and has `$0.00` balance.
14. Verify the second invoice has two credit notes with amounts `$60.00` and `$40.00`.

## Expected Result
- EU strict invoice credit notes are created for full and partial refunds.
- Credit note count, PDF availability, and amounts match the legacy regression coverage.

## Context Updates
- Save created invoice ids, titles, numbers, payment/refund status, and credit note amounts for debugging.
