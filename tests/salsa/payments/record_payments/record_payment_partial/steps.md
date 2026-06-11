# Record Partial Payment

## Objective
Record a partial payment and verify remaining balance.

## Prerequisites
- An invoice exists and is sent
- No payment gateway connected

## Steps
1. Navigate to the invoice details
2. Choose "Record Payment"
3. Enter partial payment amount and method
4. Save the payment

## Expected Result
- Invoice balance reflects remaining amount
- Payment record is visible in the invoice history

## Context Updates
- Save `recorded_payment_partial_amount`
