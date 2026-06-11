"""Setup for the "paying for an invoiced event" scenario (isolated account).

Mirrors the legacy Background. point_of_sale stays at its default; the invoice's
take-payment uses the record dialog regardless.
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.salsa.payments.event_payments.event_payments_api import seed_event_with_client


def setup_invoiced_event(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 2: Seed client + $10 require-to-pay event + registration (API)")
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
