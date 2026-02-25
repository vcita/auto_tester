# Send Invoice

## Objective
Send or mark an invoice as sent and verify status.

## Prerequisites
- An invoice exists (from create_invoice)
- No payment gateway connected

## Steps
1. Navigate to Invoices
2. Open the existing invoice
3. Click "Send" or "Mark as sent"
4. Confirm send action

## Expected Result
- Invoice status updates to sent

## Context Updates
- Save `sent_invoice_status`
