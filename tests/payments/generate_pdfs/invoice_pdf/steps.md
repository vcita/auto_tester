# Generate invoice PDF

Migrated from `automation-js/features/steps/generate_pdfs.feature` scenario 2
("Generate invoice PDF").

## Objective
Create an invoice via API and verify the billboard generates a PDF for it.

## Preconditions (from _setup)
- Isolated account (api_token/pivot_uid injected by the runner).
- Client "first last" created via API.

## Steps
1. Create an invoice titled `invoice` for the shared client, billing address
   `persepolis, persia`, with a `$20` item (`product_item200`).
2. Generate the invoice PDF via the billboard API (keyed by the invoice id).
3. Verify the PDF was generated successfully (non-empty base64 string).
