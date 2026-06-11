"""Setup for the "payment request created for appointment" scenario.

Mirrors the appointment-payments.feature Background: log in to the fresh
account, then via API create the client "first last", a "display a fee" $100
service, and schedule an appointment for the client.
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.salsa.payments.appointment_payments.appointment_payments_api import seed_appointment


def setup_payment_request_created(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 2: Seed client + $100 display-a-fee service + appointment (API)")
    seed_appointment(
        context,
        service_name="service",
        payment_setting="display a fee",
        price=100,
        first="first",
        last="last",
        email=f"test+{int(time.time() * 1000)}@vmeetme.com",
        identifier="service",
    )
    print("  [OK] setup complete - appointment for 'first last' on 'service'")
