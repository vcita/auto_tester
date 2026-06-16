# Script — invoice_pdf

Phase 2 (HOW). API-only; flows live in `generate_pdfs_api.py`. Endpoints confirmed
against the legacy chain (`api/invoices.js`, `api/billboard.js`).

## Step 1 — Create invoice
```python
invoice = create_invoice_via_api(
    context, title="invoice", client_id=context["pdf_client_id"], address="persepolis, persia",
)
```
`POST /platform/v1/invoices` with a single $20 item; the server assigns the numbered
title (`invoice #0000001`). The invoice id is read from the response (never hardcoded).

## Step 2 — Generate the PDF
```python
pdf = get_invoice_pdf(context, invoice["id"])
```
`GET {apigw}/business/billboard/v1/invoices/{id}/pdf` → `{data: <base64>}`.

## Step 3 — Assert generated
```python
assert_pdf_generated(pdf, "invoice")
```
Mirrors the legacy `invoice.pdf.should.be.a('string')`.
