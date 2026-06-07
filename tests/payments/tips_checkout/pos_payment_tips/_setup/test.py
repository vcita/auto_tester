"""Setup for the POS tips scenario (isolated account).

Same seed as the BO scenario but point_of_sale stays ENABLED so Quick Actions
exposes the POS (Take payment) large action. All API seeding runs before login.
"""

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.payments.tips_checkout.tips_checkout_api import seed_balance_tip_account


def setup_pos_payment_tips(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Steps 1-7: Seed tips app, BO tips, client + service + package + appointment (API)")
    seed_balance_tip_account(context, deny_pos=False)

    print("  Setup Step 8: Log in to isolated account (Account model loads tips now)")
    fn_login(page, context, username=username, password=password)
    print("  [OK] setup complete - POS tips scenario ready")
