"""Setup for the "redeem event payment request with package" scenario (isolated).

Seeds a $10 require-to-pay event and a client ("pack man") holding a package that
offers the event, registered as the sole attendee so there is a single order to
redeem.
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.salsa.payments.event_payments.event_payments_api import seed_event_package_redeem


def setup_redeem_package(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 2: Seed event + 'pack man' with an assigned package + registration (API)")
    service_name = f"r2p_event{int(time.time())}"
    seed_event_package_redeem(
        context,
        service_name=service_name,
        price=10,
        package_name="package",
        credits=2,
        package_price=150,
        first="pack",
        last="man",
        email=f"test2+{int(time.time() * 1000)}@vmeetme.com",
    )
    print(f"  [OK] setup complete - event '{service_name}', attendee 'pack man' with package")
