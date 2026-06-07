"""Setup for the CP follow-up-tip scenario (isolated account).

API-seeds tips (CP-enabled) + a require/suggest service, two past appointments, and a
recorded $100 payment for the require meeting (so it is paid and exposes "Add a tip"),
then logs in and connects the mock payment gateway.
"""

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.payments.tips_checkout.tips_checkout_api import seed_cp_followup_tip_account
from tests.payments.tips_settings.tips_gateway import connect_mock_gateway


def setup_cp_followup_tip(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Steps 1-7: Seed tips app, CP tips, services, appointments + paid meeting (API)")
    seed_cp_followup_tip_account(context)

    print("  Setup Step 8: Log in to the back office")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 9: Connect the mock payment gateway (providers UI)")
    connect_mock_gateway(page, context)
    print("  [OK] setup complete - CP follow-up tip scenario ready")
