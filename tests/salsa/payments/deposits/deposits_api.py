"""API helpers for the Deposits subcategory (migrated from features/salsa/deposits.feature).

Covers the prerequisites the legacy feature created via API: payable products, an
estimate with optional signature requirement, and a deposit request attached to that
estimate. Estimate/invoice identifiers are resolved dynamically (never hardcoded to
``#0000001``) because all deposits tests share one isolated account.
"""

from datetime import datetime, timedelta, timezone

from tests.account_api import account_request


def _today_iso() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def _due_date_iso(months: int = 1) -> str:
    return (datetime.now(timezone.utc) + timedelta(days=30 * months)).date().isoformat()


def create_product(context: dict, name: str, price: str, description: str = "") -> dict:
    """Create a payable product (POST business/payments/v1/products) and return it."""
    response = account_request(
        context,
        "POST",
        "/business/payments/v1/products",
        json={
            "product": {
                "name": name,
                "description": description,
                "price": price,
                "currency": "USD",
                "display": True,
                "tax_ids": [],
            },
            "new_api": True,
        },
    )
    data = response.get("data") or response
    product = data.get("product") or data
    if not (product.get("id") or product.get("uid")):
        raise ValueError(f"Product API response did not include an id: {response}")
    product["price"] = product.get("price") or price
    product["name"] = product.get("name") or name
    return product


def create_estimate_via_api(
    context: dict,
    title: str,
    client: dict,
    products: list[dict],
    *,
    address: str = "Babylon, persia",
    send_email: bool = True,
    is_signature_required: bool = False,
) -> dict:
    """Create an estimate (POST /platform/v1/estimates) from existing products.

    Returns the created estimate dict (includes ``id``/``uid``, ``title``,
    ``conversation_id`` used as the deposit ``matter_uid``, and ``currency``).
    """
    items = [
        {
            "title": product["name"],
            "amount": product["price"],
            "quantity": 1,
            "description": product.get("description", ""),
        }
        for product in products
    ]
    payload = {
        "title": title,
        "client_id": client["id"],
        "address": address,
        "currency": "USD",
        "estimate_date": _today_iso(),
        "due_date": _due_date_iso(),
        "items": items,
        "send_email": send_email,
        "is_signature_required": is_signature_required,
    }
    response = account_request(context, "POST", "/platform/v1/estimates", json=payload)
    data = response.get("data") or response
    estimate = data.get("estimate") or data
    estimate["id"] = estimate.get("id") or estimate.get("uid")
    if not estimate["id"]:
        raise ValueError(f"Estimate API response did not include an id: {response}")
    return estimate


def create_deposit_request(
    context: dict,
    estimate: dict,
    *,
    amount: str = "10",
    deposit_type: str = "fixed",
    total: str = "10",
    can_client_pay: bool = True,
) -> dict:
    """Attach a deposit request to an estimate (POST /business/payments/v1/deposits)."""
    payload = {
        "deposit": {
            "entity_type": "Estimate",
            "entity_uid": estimate["id"],
            "matter_uid": estimate.get("conversation_id") or estimate.get("matter_uid"),
            "amount": {"type": deposit_type, "value": amount, "total": total},
            "currency": estimate.get("currency") or "USD",
            "can_client_pay": can_client_pay,
        }
    }
    response = account_request(context, "POST", "/business/payments/v1/deposits", json=payload)
    return response.get("data") or response


def latest_invoice_for_client(context: dict, client_id: str) -> dict:
    """Return the client's newest invoice as {uid, title, full_title} (dynamic, no #0000001)."""
    response = account_request(context, "GET", "/platform/v1/invoices?per_page=100")
    data = response.get("data") or response
    invoices = data.get("invoices") if isinstance(data, dict) else data
    mine = [
        invoice
        for invoice in (invoices or [])
        if (invoice.get("client_id") or (invoice.get("client") or {}).get("id")) == client_id
    ]
    if not mine:
        raise AssertionError(f"No invoices returned for client {client_id}")
    mine.sort(key=lambda invoice: invoice.get("created_at") or "", reverse=True)
    invoice = mine[0]
    return {
        "uid": invoice.get("id") or invoice.get("uid"),
        "title": invoice.get("title"),
        "number": invoice.get("invoice_number") or invoice.get("number"),
    }
