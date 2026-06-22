"""Setup for the "paying for custom fee service appointment" scenario.

Background + scenario prerequisites via API: client "first last", a
"display for a fee" (price varies) service, an API-scheduled appointment, and a
13% tax. point_of_sale stays enabled (default) so the price-varies take-payment
opens the POS sales page.
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.salsa.payments.appointment_payments.appointment_payments_api import (
    schedule_appointment,
    seed_client,
    seed_service,
    seed_tax,
)


def setup_custom_fee_service(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Log in to isolated account (point_of_sale enabled)")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 2: Seed client + 'display for a fee' (price varies) service (API)")
    seed_client(context, first="first", last="last",
                email=f"test+{int(time.time() * 1000)}@vmeetme.com")
    service = seed_service(context, name="service", payment_setting="display for a fee", price=None)

    print("  Setup Step 3: Schedule appointment for the service (API)")
    schedule_appointment(context, service=service, identifier="service")

    print("  Setup Step 4: Create 13% tax 'TStax' (API)")
    seed_tax(context, name="TStax", rate=13)
    print("  [OK] setup complete - price-varies appointment + tax for 'first last'")
