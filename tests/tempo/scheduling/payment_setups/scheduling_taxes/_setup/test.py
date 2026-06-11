"""Setup for the scheduling-with-taxes scenario (isolated account).

Mirrors the legacy Background + Given steps: connect a mock gateway (require/suggest to pay
produce DUE / NOT YET DUE payment requests only with an online payment method), create three
taxes via API (a default-for-services 10% tax + a 5% and a 15% tax), create the API-only
``suggest2pay`` service (which does NOT inherit the default tax), create the client, and log
in. The UI services and scheduling happen in the test body.
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import create_client, create_service_via_api
from tests.salsa.payments.tips_settings.tips_gateway import connect_mock_gateway
from tests.tempo.scheduling.payment_setups.payment_setups_api import create_tax
from tests.tempo.scheduling.payment_setups.payment_setups_common import charge_type_for


def setup_scheduling_taxes(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    seq = int(time.time())
    print("  Setup Step 1: Create client 'first1 last1' via API")
    client = create_client(context, "first1", "last1", f"te+{seq}@vmeetme.com")

    print("  Setup Step 2: Create taxes via API (default-for-services 10%, 5%, 15%)")
    default_tax = create_tax(context, f"default_tax{seq}", 10, default_for_categories="services")
    non_default_tax = create_tax(context, f"non_default_tax{seq}", 5)
    another_tax = create_tax(context, f"another_tax{seq}", 15)

    print("  Setup Step 3: Create API-only 'suggest2pay' service (no default tax)")
    suggest = create_service_via_api(
        context, "suggest2pay", charge_type=charge_type_for("suggest to pay"), price="50"
    )

    print("  Setup Step 4: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 5: Connect mock payment gateway (enables DUE/NOT-YET-DUE requests)")
    connect_mock_gateway(page, context)

    ps = context.setdefault("ps", {})
    ps["client"] = {"id": client["id"], "name": client.get("full_name") or "first1 last1"}
    ps["services"] = {"suggest2pay": suggest}
    ps["taxes"] = {
        "default": {"name": f"default_tax{seq}", "rate": 10, "tax": default_tax},
        "non_default": {"name": f"non_default_tax{seq}", "rate": 5, "tax": non_default_tax},
        "another": {"name": f"another_tax{seq}", "rate": 15, "tax": another_tax},
    }
    print(f"  [OK] setup complete - client + suggest2pay + 3 taxes")
