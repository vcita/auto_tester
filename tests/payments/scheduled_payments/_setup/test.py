"""Setup for the scheduled_payments subcategory.

Mirrors the legacy scheduled_payments.feature Background plus its gateway and
saved-card preconditions: enable the payments checkout/gateway rollout flags, log
in to the isolated account, create a client via API, connect a mock payment
gateway (which enables checkout so the Schedule payment quick action is available),
enable credit-card checkout via API, and save a card on file for the client.
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import create_client, enable_features
from tests.payments.card_on_file.card_on_file_api import enable_credit_card
from tests.payments.offset_fees.offset_fees_setup_ui import save_card_on_file
from tests.payments.tips_settings.tips_gateway import connect_mock_gateway

CLIENT_FIRST_NAME = "first"
CLIENT_LAST_NAME = "last"

# The redesigned payment dialogs and the gateway providers UI are gated by the
# payments checkout/gateway rollout flags (same set used by card_on_file/offset_fees).
CHECKOUT_FEATURES = ",".join(
    [
        "client_portal_checkout_v2",
        "rollout.payments.checkout_redesign",
        "rollout.payments.gateway_platform",
    ]
)


def setup_scheduled_payments(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Enable payments checkout feature flags (before login)")
    enable_features(context, CHECKOUT_FEATURES)

    print("  Setup Step 2: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 3: Create client via API")
    # Unique last name so the Quick Actions client picker stays deterministic.
    stamp = int(time.time() * 1000)
    email = f"scheduled{stamp}@vmeetme.com"
    client = create_client(context, CLIENT_FIRST_NAME, f"{CLIENT_LAST_NAME}{stamp}", email)
    context["sp_client"] = client
    context["sp_client_id"] = client["id"]
    context["sp_client_name"] = client["full_name"]

    print("  Setup Step 4: Connect mock payment gateway")
    connect_mock_gateway(page, context)

    print("  Setup Step 5: Enable credit-card checkout via API")
    enable_credit_card(context)

    print("  Setup Step 6: Save a credit card on file for the client")
    save_card_on_file(page, context, client["id"])

    print(f"  [OK] scheduled_payments setup complete - client '{client['full_name']}' ready with saved card")
