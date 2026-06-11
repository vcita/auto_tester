# Record Multiple Payments

## Objective
Record multiple payments for the same invoice and verify cumulative balance.

## Prerequisites
- An invoice exists and is sent
- No payment gateway connected

## Steps
1. Navigate to the invoice details
2. Record the first payment
3. Record a second payment
4. Verify cumulative balance and payment history

## Expected Result
- Invoice balance reflects total of recorded payments
- Multiple payment records are visible

## Context Updates
- Save `recorded_payment_first_amount`, `recorded_payment_second_amount`
