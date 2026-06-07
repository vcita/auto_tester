"""Setup for the CP pay-link tips scenario (isolated account).

API-seeds tips (CP-enabled) + a suggest-to-pay service + a client with a payable past
appointment, then logs in and connects the mock payment gateway (required for the CP
checkout to render the tip bar and accept payment).
"""

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.payments.tips_checkout.tips_checkout_api import seed_cp_tip_account
from tests.payments.tips_settings.tips_gateway import connect_mock_gateway


def setup_cp_paylink_tips(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Steps 1-6: Seed tips app, CP tips, service, client + past appointment (API)")
    seed_cp_tip_account(context)

    print("  Setup Step 7: Log in to the back office")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 8: Connect the mock payment gateway (providers UI)")
    connect_mock_gateway(page, context)
    print("  [OK] setup complete - CP pay-link tips scenario ready")
