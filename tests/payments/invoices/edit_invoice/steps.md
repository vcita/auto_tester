# Edit Invoice

## Objective
Edit an existing invoice and verify totals update.

## Prerequisites
- An invoice exists (from create_invoice)
- No payment gateway connected

## Steps
1. Navigate to Invoices
2. Open the existing invoice
3. Edit line items or quantities
4. Save changes

## Expected Result
- Invoice totals reflect the changes

## Context Updates
- Update `created_invoice_amount`
