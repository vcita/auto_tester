"""Setup for the coupons_checkout subcategory (isolated account).

Mirrors the account-level prerequisites of the legacy coupons-pay.feature Background:
log in to the isolated account, create a 20% tax, two "suggest to pay" ($100) appointment
services ("appointment_1"/"appointment_2") taxed with it, and connect the mock payment
gateway. The consumable prerequisites (client + the two PAST appointments whose balance
each scenario pays) are created per-test, because paying a balance consumes it and all
four tests share this one account.
"""

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.salsa.payments.coupons_checkout.coupons_checkout_api import (
    create_tax,
    create_taxed_paid_service,
)
from tests.salsa.payments.tips_settings.tips_gateway import connect_mock_gateway

SERVICE_NAMES = ["appointment_1", "appointment_2"]


def setup_coupons_checkout(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 2: Create 20% tax 'TS' via API")
    tax = create_tax(context)
    context["checkout_tax"] = tax

    print("  Setup Step 3: Create 2 taxed 'suggest to pay' ($100) services via API")
    services = {
        name: create_taxed_paid_service(context, name, [tax["id"]]) for name in SERVICE_NAMES
    }
    context["checkout_services"] = services

    print("  Setup Step 4: Connect mock payment gateway (UI)")
    connect_mock_gateway(page, context)

    print(f"  [OK] coupons_checkout setup complete - tax + {len(services)} taxed services + mock gateway ready")
