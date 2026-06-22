"""Setup for the cp_payment_actions subcategory (isolated account).

Mirrors the legacy cp/payment-actions.feature Background: deny point_of_sale, log in,
connect the mock payment gateway, create a "display a fee" ($100) service and a client.
Saves the service + client (with portal token) under context["cp_payment_actions"] for
both tests to consume.
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import (
    create_client,
    create_service_via_api,
    deny_features,
)
from tests.salsa.payments.tips_settings.tips_gateway import connect_mock_gateway


def setup_cp_payment_actions(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    store = context.setdefault("cp_payment_actions", {})
    seq = int(time.time() * 1000)

    print("  Setup Step 1: Deny the point_of_sale feature flag (API)")
    deny_features(context, "point_of_sale")

    print("  Setup Step 2: Log in to the isolated back office")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 3: Connect the mock payment gateway (providers UI)")
    connect_mock_gateway(page, context)

    print("  Setup Step 4: Create a 'display a fee' ($100) service via API")
    service_name = f"service{seq}"
    service = create_service_via_api(
        context, service_name, charge_type="paid_non_secured", price="100"
    )
    store["service"] = service

    print("  Setup Step 5: Create a client via API")
    client = create_client(context, "first", "last", f"test+{seq}@vmeetme.com")
    store["client"] = {
        "id": client["id"],
        "name": client.get("full_name") or "first last",
        "first": "first",
        "email": f"test+{seq}@vmeetme.com",
        "portal_token": client["token"],
    }

    print(f"  [OK] cp_payment_actions setup complete - service '{service['name']}' + client + mock gateway ready")
