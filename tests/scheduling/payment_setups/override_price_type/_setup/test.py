"""Setup for the override-price-type scenario (isolated account).

Mirrors the legacy scenario's "create services via API" + "log in via API" Given steps:
create the client and the six payment-setting services via API, then log in. The price
override happens in the scheduling dialog in the test body (in-scope behavior).
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import create_client, create_service_via_api
from tests.scheduling.payment_setups.payment_setups_common import charge_type_for

SERVICES = [
    ("require2pay", "require to pay", "100"),
    ("suggest2pay", "suggest to pay", "50"),
    ("displayFee", "display a fee", "10"),
    ("variedPrice", "display for a fee", None),
    ("displayFree", "display free", None),
    ("noDisplay", "dont display", None),
]


def setup_override_price_type(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    seq = int(time.time())
    print("  Setup Step 1: Create client 'first1 last1' via API")
    client = create_client(context, "first1", "last1", f"te+{seq}@vmeetme.com")

    print("  Setup Step 2: Create six payment-setting services via API")
    services = {}
    for name, setting, price in SERVICES:
        services[name] = create_service_via_api(
            context, name, charge_type=charge_type_for(setting), price=price
        )

    print("  Setup Step 3: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    ps = context.setdefault("ps", {})
    ps["client"] = {"id": client["id"], "name": client.get("full_name") or "first1 last1"}
    ps["services"] = services
    print(f"  [OK] setup complete - client + {len(services)} services")
