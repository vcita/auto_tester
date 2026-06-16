"""Setup for the client_create_paths subcategory.

Mirrors the legacy client-create-new-CRM.feature background: log in to the isolated
automatic account. The four creation channels are exercised by the test itself.
"""

from playwright.sync_api import Page

from tests._functions.login.test import fn_login


def setup_client_create_paths(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup: Log in to isolated account")
    fn_login(page, context, username=username, password=password)
