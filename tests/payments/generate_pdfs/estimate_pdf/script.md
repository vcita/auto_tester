# Script — estimate_pdf

Phase 2 (HOW). API-only; flows live in `generate_pdfs_api.py`. Endpoints confirmed
against the legacy chain (`api/estimate.js`, `api/billboard.js`).

## Step 1 — Create estimate
```python
estimate = create_estimate_via_api(
    context, title="estimate", client_id=context["pdf_client_id"], address="persepolis, persia",
)
```
`POST /platform/v1/estimates` with a single $20 item; the server assigns the numbered
title (`estimate #0000001`). The estimate id is read from the response (never hardcoded).

## Step 2 — Generate the PDF
```python
pdf = get_estimate_pdf(context, estimate["id"])
```
`GET {apigw}/business/billboard/v1/estimates/{id}/pdf` → `{data: <base64>}`. The getter
retries briefly if the billboard 404s/empties while the estimate propagates.

## Step 3 — Assert generated
```python
assert_pdf_generated(pdf, "estimate")
```
Mirrors the legacy `estimate.pdf.should.be.a('string')` — a non-empty base64 string.
