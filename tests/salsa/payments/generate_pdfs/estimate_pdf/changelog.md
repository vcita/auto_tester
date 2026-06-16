# Changelog — estimate_pdf

## 2026-06-07 — Initial migration (VCITA2-13902)
- Migrated generate_pdfs.feature scenario 1 (Generate estimate PDF).
- Creates an estimate via API ($20 item) and verifies the billboard returns a non-empty
  PDF. Estimate id resolved dynamically from the create response (no hardcoded #0000001).
