"""Setup for the card_on_file subcategory.

Mirrors the legacy card-on-file.feature Background plus its gateway precondition:
log in to the isolated account, create a client via API, and connect a mock
payment gateway (a connected gateway is required before a card-on-file request
can be sent).
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import enable_features
from tests.salsa.payments.card_on_file.card_on_file_api import create_client, enable_credit_card
from tests.salsa.payments.tips_settings.tips_gateway import connect_mock_gateway

CLIENT_FIRST_NAME = "first"
CLIENT_LAST_NAME = "last"

# The redesigned add-payment-method dialog (with the "Request card" segment) is
# gated by the payments checkout/gateway rollout; `cof_invite` is the card-on-file
# invite feature that lets the gateway accept a client card-on-file request. These
# mirror the legacy automation-js default account flags for this feature.
CARD_ON_FILE_FEATURES = ",".join(
    [
        "cof_invite",
        "client_portal_checkout_v2",
        "rollout.payments.checkout_redesign",
        "rollout.payments.gateway_platform",
    ]
)


def setup_card_on_file(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Enable payments checkout feature flags (before login)")
    enable_features(context, CARD_ON_FILE_FEATURES)

    print("  Setup Step 2: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 3: Create client via API")
    # The request is sent to the client's stored email, so use a plain unique
    # address (no plus-addressing) to keep the destination unambiguous.
    email = f"cardonfile{int(time.time() * 1000)}@vmeetme.com"
    client = create_client(context, CLIENT_FIRST_NAME, CLIENT_LAST_NAME, email)
    context["card_on_file_client"] = client
    context["card_on_file_client_id"] = client["id"]
    context["created_client_name"] = client["full_name"]

    print("  Setup Step 4: Connect mock payment gateway")
    connect_mock_gateway(page, context)

    print("  Setup Step 5: Enable credit-card checkout via API")
    enable_credit_card(context)

    print(f"  [OK] card_on_file setup complete - client '{client['full_name']}' ready, mock gateway connected")
