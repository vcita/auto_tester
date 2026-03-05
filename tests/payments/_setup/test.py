# Auto-generated from script.md
# Last updated: 2026-02-19
# Source: tests/payments/_setup/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

from playwright.sync_api import Page

from tests._functions.login.test import fn_login


def setup_payments(page: Page, context: dict) -> None:
    """
    Setup for payments category tests.

    Logs in to prepare for payments category tests.

    Credentials: from context (injected by runner from config.yaml target.auth). No fallbacks.

    Saves to context:
    - logged_in_user: The username that was logged in
    """
    username = context.get("username")
    password = context.get("password")
    if not username or not password:
        raise ValueError(
            "username and password not in context. Set target.auth.username and target.auth.password in config.yaml."
        )

    # Step 1: Login
    print("  Step 1: Logging in...")
    fn_login(page, context, username=username, password=password)

    print("  Payments setup complete - user is logged in")
