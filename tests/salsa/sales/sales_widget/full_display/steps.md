# Sales Widget — Full Display

## Objective
With real revenue, a pending estimate, and overdue appointment fees, the Sales widget shows the correct aggregated values and each value navigates to its back-office page.

## Prerequisites
- Isolated account with the `new_dashboard` flag, logged in (from `_setup`).
- Runs after `empty_state` (same account).

## Steps
1. Create a client via API.
2. Create three "display a fee" services ($10/$40/$30) and schedule one appointment each at 2, 9, and 35 days in the past (so each fee is overdue in a different age bucket).
3. Create a product ($80) and a signature-required estimate (with a deposit) for the client.
4. Create an invoice and record a $10 cash payment for it.
5. Open the new dashboard and read the Sales widget.
6. Click total revenue, then pending estimates, then overdue payments.

## Expected Result
- Sales widget shows: total revenue `$10.00`, pending estimates `1`, overdue payments `$80.00` with breakdowns `1-7 days / 1 payments / $10.00`, `8-30 days / 1 payments / $40.00`, `31+ days / 1 payments / $30.00`.
- Total revenue navigates to the Payments Received page; pending estimates to the Estimates page; overdue payments to the Billing & Invoicing page.

## Context Updates
- None (terminal test of the subcategory).
