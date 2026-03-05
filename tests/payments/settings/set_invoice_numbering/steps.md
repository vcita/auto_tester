# Set Invoice Numbering

## Objective
Configure invoice numbering and verify it appears on new invoices.

## Prerequisites
- Access to Payments settings
- No payment gateway connected

## Steps
1. Use an existing client from the invoice client picker
2. Navigate to Payments settings
3. Open invoice numbering settings by starting a new invoice
4. Search and select the first matching existing client in the invoice client picker
5. Configure numbering format and prefix
6. Add a line item to make the invoice valid
7. Save settings
8. Verify the new invoice uses the configured number format

## Expected Result
- Invoice numbering settings are saved
- New invoice uses the configured format

## Context Updates
- Save `configured_invoice_prefix` and `created_invoice_number`
