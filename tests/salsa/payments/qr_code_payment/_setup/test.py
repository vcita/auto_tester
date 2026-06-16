"""Setup for the QR Code Payment subcategory (isolated account).

Mirrors the legacy qr-code-payment.feature Background: enable client_portal_checkout_v2,
log in, create the client "first last" and the paid service "service-pay+<ts>" via API.

client_portal_checkout_v2 is enabled BEFORE login because feature flags are read into
the session at login time (the POS "Pay with QR code" action is gated by this flag).
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import create_client, create_service_via_api, enable_features

CLIENT_FIRST_NAME = "first"
CLIENT_LAST_NAME = "last"
SERVICE_PRICE = "100"


def setup_qr_code_payment(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Enable client_portal_checkout_v2 (before login)")
    enable_features(context, "client_portal_checkout_v2")

    print("  Setup Step 2: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    stamp = int(time.time() * 1000)

    print("  Setup Step 3: Create client 'first last' via API")
    email = f"test+{stamp}@vmeetme.com"
    client = create_client(context, CLIENT_FIRST_NAME, CLIENT_LAST_NAME, email)
    context["qr_client_name"] = client["full_name"]
    context["qr_client_email"] = email
    context["qr_client_first_name"] = CLIENT_FIRST_NAME

    print("  Setup Step 4: Create paid service 'service-pay+<ts>' via API (display a fee, $100)")
    service_name = f"service-pay+{stamp}"
    service = create_service_via_api(
        context, service_name, charge_type="paid_non_secured", price=SERVICE_PRICE
    )
    context["qr_service_name"] = service["name"]

    print(
        f"  [OK] setup complete - client '{client['full_name']}' ({email}), "
        f"service '{service['name']}' ready"
    )
