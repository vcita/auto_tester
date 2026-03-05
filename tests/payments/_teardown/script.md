# Payments Teardown - Detailed Script

> **Status**: Drafted for record-payments-only stage
> **Last Updated**: 2026-02-12

## Initial State
- User is logged in.
- Payments tests may have created invoices or payments.

## Actions

### Step 1: Navigate to Billing & Invoicing
- **Action**: Open Sales -> Billing & Invoicing.

### Step 2: Cancel test invoices when possible
- **Action**: If `created_invoice_id` exists, open invoice and cancel via actions menu.

### Step 3: Clear context
- **Action**: Remove `created_*`, `recorded_*`, `configured_*`, and `issued_*` keys.

## Success Verification
- Context is cleared.
- Invoices are canceled when possible.

