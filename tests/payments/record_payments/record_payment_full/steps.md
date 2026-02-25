# Record Full Payment

## Objective
Record a full payment for an invoice and verify the balance is zero.

## Prerequisites
- An invoice exists and is sent
- No payment gateway connected

## Steps
1. Navigate to the invoice details
2. Choose "Record Payment"
3. Enter full payment amount and method
4. Save the payment

## Expected Result
- Invoice balance is zero
- Payment record is visible in the invoice history

## Context Updates
- Save `recorded_payment_id`, `recorded_payment_amount`, `recorded_payment_method`
