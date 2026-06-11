"""Setup for the Dashboard category.

Enables the new_dashboard feature flag and logs in. Mirrors the legacy
quick-actions-widget Background (account with new_dashboard FF + login).
"""

from playwright.sync_api import Page

from tests.account_api import enable_features
from tests._functions.login.test import fn_login


def setup_dashboard(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("username and password are missing from context")

    print("  Step 1: Enabling new_dashboard feature flag...")
    enable_features(context, "new_dashboard")

    print("  Step 2: Logging in...")
    fn_login(page, context, username=username, password=password)
    print(f"  [OK] dashboard setup complete - logged in as {context.get('logged_in_user')}")
