"""Setup for invoice_late_fee_ui.

Mirrors the legacy Background:
  Given user logged in to automatic account (United States)
  And user creates new client via API (first last)
  And user creates new service via API ("display a fee", price 100)

Uses account_api.create_client so the client's portal JWT token is captured (needed for
the client-portal step). The US country comes from the isolated account_profile.
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import create_client, create_service_via_api

SERVICE_PRICE = "100"


def setup_invoice_late_fee_ui(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Step 1: Log in to isolated US account")
    fn_login(page, context, username=username, password=password)

    email = f"test+{int(time.time())}@vmeetme.com"
    print("  Step 2: Create 'first last' client via API (captures portal token)")
    client = create_client(context, "first", "last", email)
    context["created_client_id"] = client["id"]
    context["created_client_name"] = client["full_name"]
    context["created_client_email"] = client.get("email") or email
    context["client_portal_token"] = client["token"]

    print("  Step 3: Create 'display a fee' service ($100) via API")
    service = create_service_via_api(
        context, f"service{int(time.time())}",
        charge_type="paid_non_secured", price=SERVICE_PRICE,
    )
    context["invoice_service_name"] = service["name"]
    print(f"  Setup complete - client={context['created_client_id']} service={service['name']}")
