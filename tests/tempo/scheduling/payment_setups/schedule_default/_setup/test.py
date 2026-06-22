"""Setup for the schedule-service-default scenario (isolated account).

Mirrors the legacy payment-setups Background: create a client via API, log in, and
connect a mock payment gateway. The gateway is a prerequisite (not the behavior under
test): the legacy automation account has an online payment method, so "require to pay"
renders its price/"required" type; a bare isolated account would degrade it. The six
services are created through the UI in the test body (in-scope behavior).
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import create_client
from tests.salsa.payments.tips_settings.tips_gateway import connect_mock_gateway


def setup_schedule_default(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    seq = int(time.time())
    print("  Setup Step 1: Create client 'first1 last1' via API")
    client = create_client(context, "first1", "last1", f"te+{seq}@vmeetme.com")

    print("  Setup Step 2: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 3: Connect mock payment gateway (enables 'require to pay')")
    connect_mock_gateway(page, context)

    context.setdefault("ps", {})["client"] = {
        "id": client["id"],
        "name": client.get("full_name") or "first1 last1",
    }
    print(f"  [OK] setup complete - client '{context['ps']['client']['name']}'")
