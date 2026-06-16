"""Setup for the "Schedule appointment with packaged service" scenario.

Background + scenario prerequisites via API: client "first last", a "display a
fee" $100 service, two scheduled appointments (meeting1, meeting2), and a
2-credit $150 package offering the service, assigned to the client. The legacy
scenario schedules the appointments through the UI to pick the
redeem-with-package option; here the appointments are API-seeded and the
redeem / complete / cancel-redemption actions are exercised in the UI (the
package-redemption behavior under test), with the UI scheduling dialog treated
as an out-of-scope prerequisite.
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.salsa.payments.appointment_payments.appointment_payments_api import (
    schedule_appointment,
    seed_client,
    seed_package,
    seed_service,
)


def setup_packaged_service(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 2: Seed client + $100 display-a-fee service (API)")
    seed_client(context, first="first", last="last",
                email=f"test+{int(time.time() * 1000)}@vmeetme.com")
    service = seed_service(context, name="service", payment_setting="display a fee", price=100)

    print("  Setup Step 3: Schedule meeting1 + meeting2 earlier today (API)")
    schedule_appointment(context, service=service, identifier="meeting1", lead_days=0)
    schedule_appointment(context, service=service, identifier="meeting2", lead_days=0)

    print("  Setup Step 4: Create 2-credit $150 package offering 'service' + assign to client (API)")
    seed_package(context, name="package", service=service, credits=2, price=150)
    print("  [OK] setup complete - meeting1, meeting2 + package for 'first last'")
