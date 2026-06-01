"""Setup for the qr_code subcategory.

Mirrors the legacy qr-code-payment.feature Background plus its gateway precondition:
enable the checkout flag, log in to the isolated account, connect the mock payment
gateway, and create the client + a "display a fee" ($100) appointment service.
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import create_client, create_service, enable_features
from tests.payments.tips_settings.tips_gateway import connect_mock_gateway

CLIENT_FIRST_NAME = "first"
CLIENT_LAST_NAME = "last"
SERVICE_PRICE = "100"
# Legacy payment_setting "display a fee" maps to this charge type.
DISPLAY_A_FEE = "paid_non_secured"
# The Pay-with-QR / link checkout is gated by the v2 client-portal checkout flag,
# mirroring the legacy account FF for this feature.
QR_FEATURES = "client_portal_checkout_v2"


def setup_qr_code(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Enable client_portal_checkout_v2 (before login)")
    enable_features(context, QR_FEATURES)

    print("  Setup Step 2: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 3: Create client via API")
    email = f"qrpay+{int(time.time() * 1000)}@vmeetme.com"
    client = create_client(context, CLIENT_FIRST_NAME, CLIENT_LAST_NAME, email)
    context["created_client_name"] = client["full_name"]

    print("  Setup Step 4: Create 'display a fee' $100 appointment service via API")
    service_name = f"service-pay-{int(time.time() * 1000)}"
    create_service(context, service_name, DISPLAY_A_FEE, SERVICE_PRICE)
    context["qr_service_name"] = service_name

    print("  Setup Step 5: Connect mock payment gateway")
    connect_mock_gateway(page, context)

    print(f"  [OK] qr_code setup complete - client '{client['full_name']}', service '{service_name}', mock gateway connected")
