"""API helpers for the Generate PDFs migration (VCITA2-13902).

Migrated from automation-js features/steps/generate_pdfs.feature. Every step in that
feature is API-only, so this module mirrors the legacy backing APIs:

  - api/estimate.create_estimate   -> create_estimate_via_api (inline items)
  - api/invoices.create_invoice    -> create_invoice_via_api  (inline items)
  - api/payments.create_payment    -> record_payment ("Payment for {paying_for}")
  - api/billboard.get_*_pdf        -> get_{estimate,invoice,receipt}_pdf

Billboard PDFs live on the API gateway (not the core API), so the PDF getters route
through the proven `_apigw_base` resolver. Each endpoint returns
``{"data": "<base64>", "content_type": "application/pdf"}``; success is a non-empty
base64 string (mirrors the legacy chai check `pdf.should.be.a('string')`).

Entity identifiers are taken from each create response (never hardcoded to ``#0000001``)
so the three subcategories can safely share one isolated account.
"""

import time
from datetime import datetime, timedelta, timezone

import requests

from tests.account_api import account_request
from tests.salsa.payments.invoices.invoice_billing_api import _apigw_base

# The billboard renders the PDF on demand; immediately after an entity is created the
# first request can briefly 404/5xx while the entity propagates. Bounded short retry.
PDF_RETRIES = 4
PDF_RETRY_DELAY_S = 1.0


def _today_iso() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def _due_date_iso(months: int = 1) -> str:
    return (datetime.now(timezone.utc) + timedelta(days=30 * months)).date().isoformat()


def _single_item(name: str, price: str, description: str) -> list[dict]:
    return [{"title": name, "amount": price, "quantity": 1, "description": description}]


def create_estimate_via_api(
    context: dict, *, title: str, client_id: str, address: str,
    item_name: str = "product_item200", price: str = "20", description: str = "short desc",
) -> dict:
    """Create an estimate (POST /platform/v1/estimates) and return it (incl. server title)."""
    payload = {
        "title": title,
        "client_id": client_id,
        "address": address,
        "currency": "USD",
        "estimate_date": _today_iso(),
        "due_date": _due_date_iso(),
        "items": _single_item(item_name, price, description),
        "send_email": False,
        "is_signature_required": False,
    }
    response = account_request(context, "POST", "/platform/v1/estimates", json=payload)
    data = response.get("data") or response
    estimate = data.get("estimate") or data
    estimate["id"] = estimate.get("id") or estimate.get("uid")
    if not estimate["id"]:
        raise ValueError(f"Estimate API response did not include an id: {response}")
    return estimate


def create_invoice_via_api(
    context: dict, *, title: str, client_id: str, address: str,
    item_name: str = "product_item200", price: str = "20", description: str = "short desc",
) -> dict:
    """Create an invoice (POST /platform/v1/invoices) and return it (incl. server title)."""
    payload = {
        "title": title,
        "client_id": client_id,
        "address": address,
        "currency": "USD",
        "due_date": _due_date_iso(),
        "issued_at": datetime.now(timezone.utc).isoformat(),
        "items": _single_item(item_name, price, description),
        "send_email": False,
        "allow_online_payment": False,
        "enable_late_fee": False,
    }
    response = account_request(context, "POST", "/platform/v1/invoices", json=payload)
    data = response.get("data") or response
    invoice = data.get("invoice") or data
    invoice["id"] = invoice.get("id") or invoice.get("uid")
    if not invoice["id"]:
        raise ValueError(f"Invoice API response did not include an id: {response}")
    return invoice


def record_payment(
    context: dict, *, paying_for: str, client_id: str, amount: str, subject_id: str,
    subject_type: str = "Invoice", method: str = "Cash",
) -> dict:
    """Record a payment (POST /platform/v1/payments).

    Title mirrors the legacy `Payment for {paying_for}`. Returns the payment dict; the
    receipt PDF is keyed by ``payment_id`` (not the invoice id), per the Platform API.
    """
    payload = {
        "title": f"Payment for {paying_for}",
        "client_id": client_id,
        "amount": amount,
        "currency": "USD",
        "payment_method": method,
        "payment_subject_id": subject_id,
        "payment_subject_type": subject_type,
    }
    response = account_request(context, "POST", "/platform/v1/payments", json=payload)
    data = response.get("data") or response
    payment = data.get("payment") or data
    payment["payment_id"] = (
        payment.get("payment_id") or payment.get("id") or payment.get("uid")
    )
    if not payment["payment_id"]:
        raise ValueError(f"Payment API response did not include a payment_id: {response}")
    return payment


def _get_pdf(context: dict, path: str) -> str:
    last_error: Exception | None = None
    for attempt in range(PDF_RETRIES):
        try:
            response = account_request(context, "GET", path, base_url=_apigw_base(context))
        except requests.HTTPError as error:
            last_error = error
            time.sleep(PDF_RETRY_DELAY_S)
            continue
        data = response.get("data") if isinstance(response, dict) else response
        # Defend against a double-enveloped body ({data: {data: <base64>}}).
        if isinstance(data, dict):
            data = data.get("data")
        if isinstance(data, str) and data.strip():
            return data
        time.sleep(PDF_RETRY_DELAY_S)
    if last_error:
        raise last_error
    return ""


def get_estimate_pdf(context: dict, estimate_id: str) -> str:
    return _get_pdf(context, f"/business/billboard/v1/estimates/{estimate_id}/pdf")


def get_invoice_pdf(context: dict, invoice_id: str) -> str:
    return _get_pdf(context, f"/business/billboard/v1/invoices/{invoice_id}/pdf")


def get_receipt_pdf(context: dict, payment_id: str) -> str:
    return _get_pdf(context, f"/business/billboard/v1/receipts/{payment_id}/pdf")


def assert_pdf_generated(pdf, label: str) -> None:
    """Assert the billboard returned a non-empty base64 PDF string (legacy parity)."""
    if not isinstance(pdf, str) or not pdf.strip():
        raise AssertionError(
            f"{label} PDF was not generated: expected a non-empty base64 string, "
            f"got {type(pdf).__name__} ({pdf!r:.80})"
        )
