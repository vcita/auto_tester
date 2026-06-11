"""Setup for the attach_document subcategory.

Mirrors the legacy attach-document-to-invoice.feature Background: log in to the
isolated account. The client and the "display a fee" service are created per-test
(see attach_to_invoice/script.md), not here.
"""

from playwright.sync_api import Page

from tests._functions.login.test import fn_login


def setup_attach_document(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup: Log in to isolated account")
    fn_login(page, context, username=username, password=password)
    print(f"  [OK] attach_document setup complete - logged in as {context.get('logged_in_user')}")
