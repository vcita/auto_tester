"""Setup for the Currency scenario (API-only, mirrors the legacy Background).

Creates the f2f service ($100) and the client used to schedule the before/after
meetings. No UI login — the whole scenario is API-driven.
"""

import time

from playwright.sync_api import Page

from tests.account_api import create_client, create_service_via_api


def setup_currency(page: Page, context: dict) -> None:
    print("  Setup Step 1: Create $100 service 'test service' via API")
    service = create_service_via_api(
        context, "test service", charge_type="paid_force", price="100",
    )
    context["currency_service"] = service

    print("  Setup Step 2: Create client 'first1 last1' via API")
    stamp = int(time.time() * 1000)
    email = f"client{stamp}@vmeetme.com"
    client = create_client(context, "first1", "last1", email)
    context["currency_client"] = client

    print("  [OK] currency setup complete - service + client ready")
