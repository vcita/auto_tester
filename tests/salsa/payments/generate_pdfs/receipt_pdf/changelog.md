# Changelog — receipt_pdf

## 2026-06-07 — Initial migration (VCITA2-13902)
- Migrated generate_pdfs.feature scenario 3 (Generate receipt PDF).
- Creates an invoice via API, records a $20 Cash payment, and verifies the billboard
  returns a non-empty receipt PDF (keyed by payment id, resolved from the payment
  response — no hardcoded #0000001).
