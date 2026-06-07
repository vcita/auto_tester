# Script — receipt_pdf

Phase 2 (HOW). API-only; flows live in `generate_pdfs_api.py`. Endpoints confirmed
against the legacy chain (`api/invoices.js`, `api/payments.js`, `api/billboard.js`).

## Step 1 — Create invoice
```python
invoice = create_invoice_via_api(
    context, title="invoice", client_id=client_id, address="persepolis, persia",
)
```

## Step 2 — Record a Cash payment
```python
payment = record_payment(
    context, paying_for=invoice["title"], client_id=client_id, amount="20",
    subject_id=invoice["id"], subject_type="Invoice",
)
```
`POST /platform/v1/payments` with title `Payment for {invoice title}`. The receipt is
keyed by `payment_id` (read from the response), not the invoice id.

## Step 3 — Generate the receipt PDF
```python
pdf = get_receipt_pdf(context, payment["payment_id"])
```
`GET {apigw}/business/billboard/v1/receipts/{payment_id}/pdf` → `{data: <base64>}`.

## Step 4 — Assert generated
```python
assert_pdf_generated(pdf, "receipt")
```
Mirrors the legacy `payment.pdf.should.be.a('string')`.
