# Generate receipt PDF

Migrated from `automation-js/features/steps/generate_pdfs.feature` scenario 3
("Generate receipt PDF").

## Objective
Create an invoice, record a payment against it, and verify the billboard generates a
receipt PDF for the payment.

## Preconditions (from _setup)
- Isolated account (api_token/pivot_uid injected by the runner).
- Client "first last" created via API.

## Steps
1. Create an invoice titled `invoice` for the shared client with a `$20` item.
2. Record a `$20` **Cash** payment against the invoice (title `Payment for invoice #...`).
3. Generate the receipt PDF via the billboard API (keyed by the **payment id**, not the
   invoice id).
4. Verify the PDF was generated successfully (non-empty base64 string).
