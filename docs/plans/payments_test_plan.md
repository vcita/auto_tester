# Payments Test Plan

## Research Summary

Notes:
- This plan targets the Payments module with record payments only.
- Online payments and payment gateway connection are explicitly out of scope for this stage.
- This summary should be validated against the product UI and vcita support docs before implementation.

Discovered/assumed feature areas:
- Invoices: create, edit, send, cancel/void, mark as unpaid, view status and history.
- Record payments: full payment, partial payment, and multiple payments against one invoice.
- Refunds and credits: record a refund or credit note against a recorded payment (if supported without PGW).
- Settings: taxes, invoice numbering, default terms, payment reminders, receipt settings.
- Client invoice access: view invoices and download (no online payment).
- Integrations: excluded for now due to no PGW connection.

## Category Structure

Top-level category:
- `tests/payments/`
  - `_setup/`
  - `_teardown/`

Proposed subcategories:
- `invoices/` (create, edit, send, cancel/void, view/download)
- `record_payments/` (record full/partial payment, multiple payments, mark unpaid)
- `refunds_credits/` (record refund or credit note when available)
- `settings/` (taxes, numbering, terms, receipts)

## Execution Order

Parent `tests/payments/_category.yaml` execution order (proposed):
1. `settings`
2. `invoices`
3. `record_payments`
4. `refunds_credits`

Rationale:
- Configure settings before creating invoices and recording payments.
- Record payments depends on invoices.
- Refunds/credits depend on recorded payments.
- Client invoice verification runs in `invoices` after invoice artifacts are created.

## Context Flow

Shared context variables (examples):
- `created_invoice_id`, `created_invoice_number`, `created_invoice_amount`
- `recorded_payment_id`, `recorded_payment_amount`, `recorded_payment_method`
- `recorded_refund_id`, `recorded_refund_amount`

Cleanup expectations:
- `_teardown` cancels or voids created invoices and clears context.
- Refund/credit records should be removed or marked as voided if possible.

## Dependencies and Risks

External dependencies:
- Email delivery for invoice sending (can be validated by UI status only).
- Client portal access (requires a client user or portal access link).

Out of scope for this stage:
- Payment gateway setup and online payment collection.
- Processor-specific flows (Stripe, PayPal, etc).

Risk notes:
- Refund/credit workflows may require PGW for online payments; if so, record-only flows should be used or the tests should be deferred.

## Test List and Priorities

Invoices (high):
- `create_invoice` - Create a new invoice with line items and tax.
- `edit_invoice` - Update line items and total.
- `send_invoice` - Send or mark as sent; verify status.
- `cancel_invoice` - Void or cancel invoice and verify status.

Record Payments (high):
- `record_payment_full` - Record full payment against an invoice; verify balance is zero.
- `record_payment_partial` - Record partial payment; verify remaining balance.
- `record_payment_multiple` - Record additional payment; verify cumulative balance.
- `mark_unpaid` - Mark payment as unpaid; verify status and balance.

Refunds/Credits (medium):
- `record_refund` - Record a refund against a recorded payment; verify balance adjustment.
- `issue_credit_note` - Issue credit note and apply to invoice if supported.

Settings (medium):
- `set_tax_rates` - Add tax and apply to invoices.
- `set_invoice_numbering` - Configure numbering and verify on new invoice.
- `set_payment_terms` - Set default terms and verify on new invoice.
- `set_receipts` - Configure receipt settings (if available without PGW).

Client Access (low/medium):
- `view_download_invoice` - Client can view and download invoice in a single flow.

## Implementation Notes

- Implement and run one test at a time in execution order.
- Tests should validate data in the UI, not toast messages.
- For any flow that appears to require a connected gateway, pause and mark the test as blocked until scope expands.
