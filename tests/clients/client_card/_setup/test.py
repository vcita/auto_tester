"""Setup for the Client Card subcategory (isolated account).

Mirrors the legacy client-card.feature Background ("user logged in to automatic
account"): log in to the fresh isolated account so each run starts with no custom
fields and a deterministic CRM list.
"""

from playwright.sync_api import Page

from tests._functions.login.test import fn_login


def setup_client_card(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    print("  [OK] setup complete - logged in to fresh account")
