"""Setup for the Orders Filter subcategory (isolated account).

Mirrors the legacy orders.feature Background (all API): log in to the isolated
account and create the client "first last" plus the paid service "service"
($100, "require to pay" -> charge_type paid_force). Fixed names are safe because
the account is fresh per run, which also keeps the Orders list deterministic.
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import create_client, create_service_via_api

CLIENT_FIRST_NAME = "first"
CLIENT_LAST_NAME = "last"
SERVICE_NAME = "service"
SERVICE_PRICE = "100"
SERVICE_CURRENCY = "USD"


def setup_orders_filter(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 2: Create client 'first last' via API")
    email = f"test+{int(time.time() * 1000)}@vmeetme.com"
    client = create_client(context, CLIENT_FIRST_NAME, CLIENT_LAST_NAME, email)

    print("  Setup Step 3: Create paid service 'service' via API (require to pay, $100)")
    service = create_service_via_api(
        context, SERVICE_NAME, charge_type="paid_force", price=SERVICE_PRICE
    )

    context["orders_client"] = {"id": client["id"], "name": client["full_name"], "email": email}
    context["orders_service"] = {
        "id": service["id"],
        "name": service["name"],
        "price": SERVICE_PRICE,
        "currency": SERVICE_CURRENCY,
    }

    print(
        f"  [OK] setup complete - client '{client['full_name']}' ({email}), "
        f"service '{service['name']}' ($100) ready"
    )
