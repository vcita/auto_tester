"""Setup for the invoice follow-up-tip (BO charge) scenario (isolated account).

API-seeds tips (BO-enabled) + a $20 invoice with a recorded $20 Cash payment (so it is
paid and exposes "Add a tip"), then logs in and connects the mock payment gateway
(required for the charge tip).
"""

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.salsa.payments.tips_checkout.tips_checkout_api import seed_invoice_followup_tip_account
from tests.salsa.payments.tips_settings.tips_gateway import connect_mock_gateway


def setup_invoice_followup_tip(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Steps 1-6: Seed tips app, BO tips, invoice + paid payment (API)")
    seed_invoice_followup_tip_account(context)

    print("  Setup Step 7: Log in to the back office")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 8: Connect the mock payment gateway (providers UI)")
    connect_mock_gateway(page, context)
    print("  [OK] setup complete - invoice follow-up tip scenario ready")
