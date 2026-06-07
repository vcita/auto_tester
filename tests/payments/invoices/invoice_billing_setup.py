"""Shared account seeding for the invoice billing migration (VCITA2-13900).

Mirrors the legacy invoices.feature Background: log in, create the `first last`
client, the paid "display a fee" service ($100), and the 13% tax. Each migrated
scenario runs on its own isolated United-States account.
"""
import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import create_service_via_api
from tests.payments.invoices.invoice_billing_api import create_tax_via_api

SERVICE_PRICE = "100"
TAX_RATE = "13"


def _create_client(context: dict) -> None:
    from tests.account_api import account_request

    stamp = int(time.time())
    response = account_request(context, "POST", "/platform/v1/clients", json={
        "first_name": "first",
        "last_name": "last",
        "email": f"test+{stamp}@vmeetme.com",
        "address": "blablablabla",
        "source_name": "automation",
    })
    payload = response.get("data") or response
    client = payload.get("client") or payload
    client_id = client.get("id") or client.get("uid")
    if not client_id:
        raise ValueError(f"Client API response did not include an id: {response}")
    context["created_client_id"] = client_id
    context["created_client_name"] = "first last"
    context["created_client_email"] = client.get("email")
    context["invoice_client_search_term"] = "first last"


def seed_invoice_account(page: Page, context: dict, *, with_tax: bool = True) -> None:
    username = context.get("username")
    password = context.get("password")
    if not username or not password:
        raise ValueError("Isolated account username and password are missing from context")

    fn_login(page, context, username=username, password=password)
    _create_client(context)

    service = create_service_via_api(
        context, f"service{int(time.time())}",
        charge_type="paid_non_secured", price=SERVICE_PRICE,
    )
    context["invoice_service"] = service
    context["invoice_service_name"] = service["name"]
    context["invoice_service_price"] = SERVICE_PRICE

    if with_tax:
        tax_name = f"TS{int(time.time())}"
        create_tax_via_api(context, tax_name, TAX_RATE)
        context["invoice_tax_name"] = tax_name
        context["invoice_tax_rate"] = TAX_RATE
