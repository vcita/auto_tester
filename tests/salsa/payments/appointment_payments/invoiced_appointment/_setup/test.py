"""Setup for the "Paying for invoiced appointment" scenario.

Mirrors the appointment-payments.feature Background: log in, then via API create
the client "first last", a "require to pay" $100 service, and schedule an
appointment for the client. (The scenario seeds require-to-pay rather than the
legacy "display a fee" so the appointment exposes an Orders row for POV-routed
invoice creation; see ``_open_appt_via_orders`` - the invoice->PAID behavior under
test is identical.)
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.salsa.payments.appointment_payments.appointment_payments_api import seed_appointment


def setup_invoiced_appointment(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 2: Seed client + $100 require-to-pay service + appointment (API)")
    seed_appointment(
        context,
        service_name="service",
        payment_setting="require to pay",
        price=100,
        first="first",
        last="last",
        email=f"test+{int(time.time() * 1000)}@vmeetme.com",
        identifier="service",
    )
    print("  [OK] setup complete - appointment for 'first last' on 'service'")
