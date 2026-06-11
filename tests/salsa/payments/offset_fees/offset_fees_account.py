"""Account preparation shared by the offset_fees subcategories.

Mirrors the legacy offset-fees Background: enable the offset-fee feature flags,
log in, provision a paid service + client + past appointment via API, connect a
mock payment gateway, enable ACH, and save a card on file. The business country
(United States) is set by the runner from each subcategory's account_profile.
"""

from __future__ import annotations

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import enable_features
from tests.salsa.payments.offset_fees.offset_fees_api import (
    create_client,
    create_past_appointment,
    create_paid_service,
    enable_card_and_ach,
    unique_email,
)
from tests.salsa.payments.offset_fees.offset_fees_setup_ui import save_card_on_file
from tests.salsa.payments.tips_settings.tips_gateway import connect_mock_gateway

CLIENT_FIRST_NAME = "first"
CLIENT_LAST_NAME = "last"

# Offset-fee checkout depends on the redesigned client-portal checkout, the
# offset-fee rollout, and a second (ACH/bank) payment method being available.
OFFSET_FEATURES = ",".join(
    [
        "rollout.payments.vcita_payments_offset_fees",
        "client_portal_checkout_v2",
        "ach_checkout_v2",
        "bank_debit_checkout",
        "rollout.payments.checkout_redesign",
        "rollout.payments.gateway_platform",
    ]
)


def prepare_account(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Enable offset-fee feature flags (before login)")
    enable_features(context, OFFSET_FEATURES)

    print("  Setup Step 2: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 3: Create paid ($100) appointment service via API")
    service = create_paid_service(context, name=unique_email("service").split("@")[0])
    context["offset_service"] = service
    context["offset_service_name"] = service["name"]

    print("  Setup Step 4: Create client via API (capturing portal token)")
    client = create_client(context, CLIENT_FIRST_NAME, CLIENT_LAST_NAME, unique_email("test"))
    context["offset_client"] = client
    context["created_client_name"] = client["full_name"]

    print("  Setup Step 5: Schedule a past appointment via API")
    booking = create_past_appointment(context, service, client)
    context["offset_booking_id"] = booking["id"]

    print("  Setup Step 6: Connect mock payment gateway")
    connect_mock_gateway(page, context)

    print("  Setup Step 7: Enable credit-card + ACH bank payments via API")
    enable_card_and_ach(context)

    print("  Setup Step 8: Save a credit card on file for the client")
    save_card_on_file(page, context, client.get("id") or client.get("uid"))

    print(f"  [OK] offset_fees setup complete - service '{service['name']}', client ready to pay")
