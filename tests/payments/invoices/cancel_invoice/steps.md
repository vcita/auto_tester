# Cancel Invoice

## Objective
Cancel or void an invoice and verify status.

## Prerequisites
- An invoice exists (from create_invoice)
- No payment gateway connected

## Steps
1. Navigate to Invoices
2. Open the existing invoice
3. Click "Cancel" or "Void"
4. Confirm cancellation

## Expected Result
- Invoice status updates to canceled or voided

## Context Updates
- Save `canceled_invoice_status`
