# Issue Credit Note

## Objective
Issue a credit note and apply it to an invoice if supported.

## Prerequisites
- An invoice exists
- No payment gateway connected

## Steps
1. Navigate to the invoice details
2. Choose "Issue Credit Note"
3. Enter credit amount and reason
4. Save the credit note
5. Apply credit note to the invoice if required

## Expected Result
- Credit note is visible in invoice history
- Invoice balance reflects the credit

## Context Updates
- Save `issued_credit_note_id`, `issued_credit_note_amount`
