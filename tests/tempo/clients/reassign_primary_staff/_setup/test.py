"""Setup for the isolated reassign_primary_staff subcategory.

Logs in to the fresh isolated account. The reassignment test seeds its own
client/staff/service/appointment via API, so setup only needs an authenticated
session (mirrors the legacy reassign-matter-primary-staff.feature Background).
"""

from playwright.sync_api import Page

from tests._functions.login.test import fn_login


def setup_reassign_primary_staff(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup: Log in to isolated account")
    fn_login(page, context, username=username, password=password)
    print(f"  [OK] reassign_primary_staff setup complete - logged in as {context.get('logged_in_user')}")
