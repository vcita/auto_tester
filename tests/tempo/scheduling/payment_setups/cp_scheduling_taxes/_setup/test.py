"""Setup for the CP-scheduling-with-taxes scenario (isolated account).

Mirrors the legacy Given steps: create a default-for-services 10% tax via API, create the
``suggest2pay`` service ($100, suggest to pay) with that tax attached, and log in to the
business so the test can grab the service public link. The anonymous client-portal booking
and the meeting-page assertions happen in the test body.
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import create_service_via_api
from tests.tempo.scheduling.payment_setups.payment_setups_api import create_tax
from tests.tempo.scheduling.payment_setups.payment_setups_common import charge_type_for


def setup_cp_scheduling_taxes(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    seq = int(time.time())
    print("  Setup Step 1: Create default-for-services 10% tax via API")
    default_tax = create_tax(context, f"default_tax{seq}", 10, default_for_categories="services")

    print("  Setup Step 2: Create 'suggest2pay' service ($100) with the default tax via API")
    suggest = create_service_via_api(
        context, "suggest2pay", charge_type=charge_type_for("suggest to pay"), price="100",
        tax_uids=[default_tax["id"]],
    )

    print("  Setup Step 3: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    ps = context.setdefault("ps", {})
    ps["service"] = {"id": suggest["id"], "name": "suggest2pay"}
    ps["tax"] = {"name": f"default_tax{seq}", "rate": 10, "tax": default_tax}
    print("  [OK] setup complete - default tax + taxed suggest2pay service")
