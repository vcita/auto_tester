"""Setup for the event follow-up-tip (BO record) scenario (isolated account).

API-seeds tips (BO-enabled) + a require-to-pay event with a registered attendee and a
recorded $10 Cash payment (so the attendance is paid and exposes "Add a tip"), then logs
in. No gateway is needed (the follow-up tip is recorded as Cash).
"""

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.payments.tips_checkout.tips_checkout_api import seed_event_followup_tip_account


def setup_event_followup_tip(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Steps 1-7: Seed tips app, BO tips, event + attendee + paid attendance (API)")
    seed_event_followup_tip_account(context)

    print("  Setup Step 8: Log in to the back office")
    fn_login(page, context, username=username, password=password)
    print("  [OK] setup complete - event follow-up tip scenario ready")
