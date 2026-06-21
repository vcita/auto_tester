"""Setup for the auto_client_messages subcategory.

Mirrors the legacy auto-client-messages.feature Background
(`Given user logged in to automatic account`): log in to the isolated account.
"""

from playwright.sync_api import Page

from tests._functions.login.test import fn_login


def setup_auto_client_messages(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup: Log in to isolated account")
    fn_login(page, context, username=username, password=password)
    print("  [OK] Logged in to isolated account")
