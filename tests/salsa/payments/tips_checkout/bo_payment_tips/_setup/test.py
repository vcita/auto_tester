"""Setup for the back-office tips scenario (isolated account).

Mirrors tips.feature scenario 1 Background + prerequisites: tips app, tip options
with BO enabled, a suggest-to-pay service, a specific package assigned to the
client, and a past appointment - so the close-balance combines the unpaid service
and package into a single payable balance. point_of_sale is denied so take payment
opens the legacy close-balance / record dialogs (not POS).

All API seeding runs BEFORE login: the Angular close-balance dialog reads tips from
the Account model loaded at login, so tips/enable_tips_for_bo must already be
persisted when the page first loads (otherwise showTips stays false).
"""

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.salsa.payments.tips_checkout.tips_checkout_api import seed_balance_tip_account


def setup_bo_payment_tips(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Steps 1-8: Seed tips app, BO tips, client + service + package + appointment (API)")
    seed_balance_tip_account(context, deny_pos=True)

    print("  Setup Step 9: Log in to isolated account (Account model loads tips now)")
    fn_login(page, context, username=username, password=password)
    print("  [OK] setup complete - BO tips scenario ready")
