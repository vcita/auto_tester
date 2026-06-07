"""Setup for the "pay for event" scenario (isolated account).

Mirrors the legacy event-payments.feature Background plus the scenario's
"denies feature flags: point_of_sale" so `take_payment` opens the legacy
record-payment dialog instead of Point of Sale.
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import deny_features
from tests.payments.event_payments.event_payments_api import seed_event_with_client


def setup_pay_for_event(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Deny point_of_sale (record-payment, not POS)")
    deny_features(context, "point_of_sale")

    print("  Setup Step 2: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 3: Seed client + $10 require-to-pay event + registration (API)")
    service_name = f"r2p_event{int(time.time())}"
    seed_event_with_client(
        context,
        service_name=service_name,
        price=10,
        first="first",
        last="last",
        email=f"test+{int(time.time() * 1000)}@vmeetme.com",
    )
    print(f"  [OK] setup complete - event '{service_name}' with attendee 'first last'")
