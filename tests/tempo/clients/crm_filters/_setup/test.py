"""Setup for the isolated CRM Filters subcategory.

Logs in to the fresh isolated account. Both CRM Filters tests seed their own
clients/products/custom-fields via API and UI, so setup only needs an
authenticated session (mirrors the legacy crm-filters-create-and-edit.feature
Background, which ran in a fresh per-scenario account).
"""

from playwright.sync_api import Page

from tests._functions.login.test import fn_login


def setup_crm_filters(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup: Log in to isolated account")
    fn_login(page, context, username=username, password=password)
    print(f"  [OK] crm_filters setup complete - logged in as {context.get('logged_in_user')}")
