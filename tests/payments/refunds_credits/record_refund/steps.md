# Record Refund

## Objective
Record a refund for a recorded payment and verify balance adjustment.

## Prerequisites
- An invoice with a recorded payment exists
- No payment gateway connected

## Steps
1. Navigate to the invoice details
2. Open the payment record
3. Choose "Record Refund" or "Refund"
4. Enter refund amount and save

## Expected Result
- Refund record is visible
- Invoice balance reflects the refund

## Context Updates
- Save `recorded_refund_id`, `recorded_refund_amount`
