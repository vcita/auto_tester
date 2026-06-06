"""Setup for the "paying for appointment via Point of Sale" scenario.

Mirrors the appointment-payments.feature Background: log in (point_of_sale
enabled by default), then via API create the client "first last", a "require to
pay" $100 service "service-rtp", and schedule an appointment for the client.
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.payments.appointment_payments.appointment_payments_api import seed_appointment


def setup_pay_via_pos(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Log in to isolated account (point_of_sale enabled)")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 2: Seed client + $100 require-to-pay service + appointment (API)")
    seed_appointment(
        context,
        service_name="service-rtp",
        payment_setting="require to pay",
        price=100,
        first="first",
        last="last",
        email=f"test+{int(time.time() * 1000)}@vmeetme.com",
        identifier="service-rtp",
    )
    print("  [OK] setup complete - appointment for 'first last' on 'service-rtp'")
