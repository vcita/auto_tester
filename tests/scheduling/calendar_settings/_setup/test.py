"""Setup for the calendar_settings subcategory.

Mirrors the legacy calendar-settings.feature Background: log in to the isolated
account as the owner (an admin). The legacy Background also creates a client and a
staff member; the client is never referenced by any scenario and the staff member is
only needed by `staff_permissions`, so neither is created here.
"""

from playwright.sync_api import Page

from tests._functions.login.test import fn_login


def setup_calendar_settings(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Log in to isolated account")
    fn_login(page, context, username=username, password=password)
    print("  [OK] calendar_settings setup complete")
