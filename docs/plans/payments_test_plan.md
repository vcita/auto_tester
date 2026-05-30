# Payments Test Plan

## Research Summary

Notes:
- This plan targets the Payments module, including record payments and flows that require a connected **mock** payment gateway.
- Connecting a mock payment gateway (via the legacy `configureMockPaymentGateway` flow) is in scope. Real/processor-specific gateways (Stripe, PayPal, etc.) remain out of scope.
- This summary should be validated against the product UI and vcita support docs before implementation.

Discovered/assumed feature areas:
- Invoices: create, edit, send, cancel/void, mark as unpaid, view status and history.
- Record payments: full payment, partial payment, and multiple payments against one invoice.
- Refunds and credits: record a refund or credit note against a recorded payment.
- Settings: taxes, invoice numbering, default terms, payment reminders, receipt settings, tips settings (mock gateway).
- Client invoice access: view invoices and download.
- Gateway-dependent flows: tests may connect a mock payment gateway when the scenario requires one (e.g. tips settings, card on file, offset fees, online checkout).

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

In scope (gateway):
- Connecting a mock payment gateway via the legacy `configureMockPaymentGateway` flow when a scenario requires a connected gateway.

Out of scope for this stage:
- Real/processor-specific gateways and live payment collection (Stripe, PayPal, etc).

Risk notes:
- Mock-gateway flows can touch client portal checkout and cross-window navigation; isolate these tests and prefer condition waits over fixed sleeps.

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
- `set_receipts` - Configure receipt settings.
- `set_tips` - Configure tips settings (connects a mock payment gateway).

Client Access (low/medium):
- `view_download_invoice` - Client can view and download invoice in a single flow.

## Implementation Notes

- Implement and run one test at a time in execution order.
- Tests should validate data in the UI, not toast messages.
- Flows that require a connected gateway should connect the mock gateway via the legacy `configureMockPaymentGateway` flow. Only pause/block when a flow requires a real processor (Stripe, PayPal, etc).
