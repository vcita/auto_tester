# Cancel Invoice

## Objective
Cancel or void an invoice and verify status.

## Prerequisites
- An invoice exists (from create_invoice)
- No payment gateway connected

## Steps
1. Navigate to Invoices
2. Open the existing invoice
3. If payment was recorded, mark the invoice as not cancellable after payment
4. Otherwise click "Cancel" or "Void"
5. Confirm cancellation

## Expected Result
- Invoice status updates to canceled/voided, or is marked not cancellable after payment

## Context Updates
- Save `canceled_invoice_status`
