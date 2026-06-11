"""Setup for the crm_bulk_actions subcategory.

Mirrors the legacy crm-bulk-actions.feature Background: log in to the isolated
account. Clients are created per-test (see each test's script.md), not here.
"""

from playwright.sync_api import Page

from tests._functions.login.test import fn_login


def setup_crm_bulk_actions(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup: Log in to isolated account")
    fn_login(page, context, username=username, password=password)
    print(f"  [OK] crm_bulk_actions setup complete - logged in as {context.get('logged_in_user')}")
