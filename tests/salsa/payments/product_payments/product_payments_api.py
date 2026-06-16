"""API seeds for the product_payments migration (VCITA2-13858).

Mirrors automation-js/features/salsa/products.feature Background plus per-scenario
prerequisites: a client, payable products, taxes, product assignments (product
orders) and the account ``tax_mode`` setting. UI-only prerequisites (creating a
product through the dialog, paying, invoicing) are performed in the test bodies.
"""

from __future__ import annotations

import time

from tests.account_api import account_request, create_client
from tests.salsa.products.products_account import create_tax_via_api

PRODUCTS_PATH = "/business/payments/v1/products"
PRODUCT_ORDERS_PATH = "/business/payments/v1/product_orders"
SETTINGS_PATH = "/v2/settings"


def _store(context: dict) -> dict:
    return context.setdefault("product_payments", {})


def seed_client(context: dict, *, first: str, last: str, email: str) -> dict:
    """Create the scenario client and cache it under product_payments."""
    client = create_client(context, first, last, email)
    record = {
        "id": client["id"],
        "name": client.get("full_name") or f"{first} {last}",
        "first": first,
        "email": email,
        "portal_token": client.get("token"),
    }
    _store(context)["client"] = record
    return record


def create_product_via_api(context: dict, *, name: str, price: str | int,
                           description: str = "", display: bool = True,
                           tax_ids: list[str] | None = None) -> dict:
    """Create a payable product (POST business/payments/v1/products)."""
    response = account_request(context, "POST", PRODUCTS_PATH, json={
        "product": {
            "name": name,
            "description": description,
            "price": str(price),
            "currency": "USD",
            "display": display,
            "tax_ids": tax_ids or [],
        },
        "new_api": True,
    })
    product = (response.get("data") or response).get("product") or response
    product_id = product.get("id") or product.get("uid")
    if not product_id:
        raise ValueError(f"Product API response missing id: {response}")
    record = {"id": product_id, "name": product.get("name") or name,
              "price": product.get("price", str(price))}
    _store(context).setdefault("products", {})[record["name"]] = record
    return record


def get_product_by_name(context: dict, name: str) -> dict:
    cached = _store(context).get("products", {}).get(name)
    if cached:
        return cached
    response = account_request(context, "GET", PRODUCTS_PATH)
    products = (response.get("data") or {}).get("products") or []
    for product in products:
        if product.get("name") == name:
            record = {"id": product.get("id") or product.get("uid"),
                      "name": product["name"], "price": product.get("price")}
            _store(context).setdefault("products", {})[name] = record
            return record
    raise ValueError(f"Product {name!r} not found in account")


def assign_product_via_api(context: dict, *, product_name: str,
                           tax_ids: list[str] | None = None) -> dict:
    """Assign a product to the seeded client (POST business/payments/v1/product_orders)."""
    product = get_product_by_name(context, product_name)
    client = _store(context)["client"]
    response = account_request(context, "POST", PRODUCT_ORDERS_PATH, json={
        "new_api": True,
        "product_order": {
            "client_id": client["id"],
            "product_id": product["id"],
            "price": product["price"],
            "tax_ids": tax_ids or [],
        },
    })
    order = (response.get("data") or response).get("product_order") or response
    order_id = order.get("id") or order.get("uid")
    if not order_id:
        raise ValueError(f"Product order API response missing id: {response}")
    record = {"id": order_id, "product_name": product_name,
              "client_name": client["name"]}
    _store(context).setdefault("orders", {})[product_name] = record
    _store(context)["last_order"] = record
    return record


def seed_tax(context: dict, *, name: str, rate: int | float) -> dict:
    """Create a tax and cache it by name (for tax_ids on products/orders)."""
    tax = create_tax_via_api(context, name, rate)
    tax_id = tax.get("id") or tax.get("uid")
    record = {"id": tax_id, "name": tax.get("name") or name, "rate": rate}
    _store(context).setdefault("taxes", {})[record["name"]] = record
    return record


def tax_id(context: dict, name: str) -> str:
    tax = _store(context).get("taxes", {}).get(name)
    if not tax:
        raise ValueError(f"Tax {name!r} not seeded")
    return tax["id"]


def set_tax_mode(context: dict, mode: str) -> None:
    """Set the account tax mode (PUT v2/settings {tax_mode}) - 'include'/'exclude'."""
    account_request(context, "PUT", SETTINGS_PATH, json={"tax_mode": mode})


# Legacy taxes are "TS+[seq]" (13%) and "TS 2+[seq]" (13.13%); names are made
# unique and space-free so the client-card tax-picker data-qa (tax-{name}-{rate})
# stays selectable. The rates (13 + 13.13) drive the asserted tax math.
ASSIGN_TAX_RATES = [13, 13.13]


def seed_assign_taxes(context: dict) -> list[dict]:
    """Create the two scenario taxes (13% + 13.13%) and record them for the UI
    assign step. Returns [{name, rate}] with rate as the string used in the
    tax-picker data-qa."""
    seq = int(time.time() * 1000)
    records = []
    for index, rate in enumerate(ASSIGN_TAX_RATES):
        name = f"TS{index}{seq}"
        seed_tax(context, name=name, rate=rate)
        records.append({"name": name, "rate": _rate_label(rate)})
    _store(context)["assign_taxes"] = records
    return records


def _rate_label(rate: int | float) -> str:
    """Format a rate the way the tax-picker data-qa renders it (13 -> '13')."""
    return str(int(rate)) if float(rate).is_integer() else str(rate)


def assign_taxes(context: dict) -> list[dict]:
    return _store(context).get("assign_taxes", [])


def seed_background(context: dict, *, first: str, last: str, email: str,
                    product_name: str, price: str | int) -> dict:
    """Feature Background: client + one display-in-list payable product."""
    seed_client(context, first=first, last=last, email=email)
    create_product_via_api(context, name=product_name, price=price,
                           description=f"description for {product_name}")
    return _store(context)
