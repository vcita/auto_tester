# Payments Category Teardown

## Objective
Clean up invoices, recorded payments, and related artifacts created during Payments tests.

## Steps

1. Navigate to invoices list
   - Ensure the list is visible and filters are reset

2. Void or cancel any test invoices
   - Locate test invoices created in this run
   - Void or cancel to prevent lingering balances

3. Clear recorded payment artifacts
   - Remove or reverse recorded payments if the UI allows
   - If reversal is not possible, document as cleanup limitation

4. Clear context
   - Remove any `created_*` or `recorded_*` keys from context

## Expected Result
- No active test invoices remain
- No pending recorded payments remain from the test run
- Context is cleared

## Notes
- This teardown assumes record payments only (no payment gateway)
