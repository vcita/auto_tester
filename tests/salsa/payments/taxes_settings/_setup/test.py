"""Setup for the taxes_settings subcategory: log in to the isolated account."""

from playwright.sync_api import Page

from tests._functions.login.test import fn_login


def setup_taxes_settings(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Step: Log in to isolated account")
    fn_login(page, context, username=username, password=password)
    print("  Setup complete - logged in, taxes list is empty")
