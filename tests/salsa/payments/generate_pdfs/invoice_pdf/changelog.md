# Changelog — invoice_pdf

## 2026-06-07 — Initial migration (VCITA2-13902)
- Migrated generate_pdfs.feature scenario 2 (Generate invoice PDF).
- Creates an invoice via API ($20 item) and verifies the billboard returns a non-empty
  PDF. Invoice id resolved dynamically from the create response (no hardcoded #0000001).
