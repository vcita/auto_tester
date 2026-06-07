"""Account preparation for the external-receipt gateway_setups subcategories (4 & 5).

Mirrors the legacy automation-js Background for the external-receipt scenarios:
optionally deny point_of_sale (scenario 4 records via Quick Actions, not POS), log in,
create the ``simon bolivar`` client via API, and assign the ``mockreceipts`` external
receipt app to the business. The app assignment makes recorded payments expose an
external "View receipt" link that redirects to the mock receipt URL.
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import create_client, deny_features
from tests.payments.gateway_setups.gateway_setups_api import (
    enable_wizard_flags,
    set_business_category,
)
from tests.payments.tips_checkout.tips_checkout_api import assign_app

CLIENT_FIRST_NAME = "simon"
CLIENT_LAST_NAME = "bolivar"
RECEIPT_APP_CODE = "mockreceipts"


def prepare_receipt_account(page: Page, context: dict, *, deny_pos: bool) -> None:
    """Deny POS (optional, before login), log in, create the client, assign mockreceipts."""
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    if deny_pos:
        print("  Setup: Deny point_of_sale (before login)")
        deny_features(context, "point_of_sale")

    print("  Setup: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    print("  Setup: Create client 'simon bolivar' via API")
    email = f"tes+{int(time.time() * 1000)}@vmeetme.com"
    client = create_client(context, CLIENT_FIRST_NAME, CLIENT_LAST_NAME, email)
    context["receipt_client_id"] = client["id"]
    context["receipt_client_name"] = f"{CLIENT_FIRST_NAME} {CLIENT_LAST_NAME}"
    context["receipt_client_email"] = email

    print(f"  Setup: Assign external-receipt app '{RECEIPT_APP_CODE}' via API")
    assign_app(context, RECEIPT_APP_CODE)

    print(f"  Setup complete - client '{context['receipt_client_name']}' + {RECEIPT_APP_CODE} ready")


def prepare_wizard_account(
    page: Page, context: dict, *, business_category: str | None, funnel_v1: bool = False
) -> None:
    """Enable the onboarding-wizard feature flags, optionally set business_category, log in.

    Flags + business_category are applied before login because the wizard, preliminary
    profession step and funnel-v1 upgrade path are all read into the session at login time.
    """
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print(f"  Setup: Enable wizard feature flags (funnel_v1={funnel_v1})")
    enable_wizard_flags(context, funnel_v1=funnel_v1)

    if business_category:
        print(f"  Setup: Set business_category '{business_category}' via API")
        set_business_category(context, business_category)

    print("  Setup: Log in to isolated account")
    fn_login(page, context, username=username, password=password)
    print("  Setup complete - onboarding wizard account ready")
