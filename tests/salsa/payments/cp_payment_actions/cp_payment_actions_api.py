"""API setup helpers for the cp_payment_actions subcategory (VCITA2-14227).

Migrated from automation-js features/salsa/cp/payment-actions.feature Background +
Scenario 2 API setup. Reuses the central account-API primitives in tests/account_api.py
and the existing invoice/product/package helpers; this module only adds the small,
subcategory-specific glue (invoice item shape, client_package lookup) that has no
existing reusable equivalent.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from tests.account_api import account_request, pivot_uid


def make_invoice_items(*, title: str, price: str, description: str = "",
                       taxes: list[dict] | None = None) -> list[dict]:
    """Build the invoice ``items`` payload (legacy invoiceHelper._parseItemForAPI shape).

    ``taxes`` is a list of {"name", "rate"} dicts, e.g. [{"name": "tax1", "rate": "10"}].
    """
    item: dict = {"title": title, "amount": price, "description": description, "quantity": 1}
    if taxes:
        item["taxes"] = [{"name": t["name"], "rate": t["rate"]} for t in taxes]
    return [item]


def invoice_due_date() -> datetime:
    """A due date one month out (legacy invoiceHelper._setDueDate)."""
    return datetime.now(timezone.utc) + timedelta(days=30)


def get_client_package_id(context: dict, client_id: str, package_name: str) -> str:
    """Resolve the clientPackageID for a client's assigned package by name.

    Mirrors legacy packageHelper.getClientPackageId: GET
    /platform/v1/clients/{id}/payment/client_packages, match by package name.
    """
    response = account_request(
        context, "GET", f"/platform/v1/clients/{client_id}/payment/client_packages"
    )
    data = response.get("data") or response
    client_packages = data.get("client_packages") or data
    for client_package in client_packages or []:
        if client_package.get("name") == package_name:
            cp_id = client_package.get("id") or client_package.get("uid")
            if cp_id:
                return cp_id
    raise ValueError(
        f"Client package {package_name!r} not found for client {client_id}; "
        f"got {[cp.get('name') for cp in (client_packages or [])]}"
    )
