"""Setup for the "paying for appointment" scenario (isolated account).

Mirrors the appointment-payments.feature Background plus the scenario's
"denies feature flags: point_of_sale" so `take_payment` opens the legacy
record-payment dialog instead of Point of Sale.
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import deny_features
from tests.payments.appointment_payments.appointment_payments_api import seed_appointment


def setup_pay_for_appointment(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Deny point_of_sale (record-payment, not POS)")
    deny_features(context, "point_of_sale")

    print("  Setup Step 2: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 3: Seed client + $100 display-a-fee service + appointment (API)")
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
