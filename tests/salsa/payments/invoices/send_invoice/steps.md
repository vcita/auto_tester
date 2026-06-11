# Record Invoice Payment

## Objective
Record a cash payment from an issued invoice and verify the action completes.

## Prerequisites
- An invoice exists (from create_invoice)
- No payment gateway connected

## Steps
1. Navigate to Invoices
2. Open the existing invoice
3. Click "Take payment"
4. Select "Record payment"
5. Record a small cash payment

## Expected Result
- Payment is recorded successfully

## Context Updates
- Save `recorded_invoice_payment_status`
