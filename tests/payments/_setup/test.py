# Auto-generated from script.md
# Last updated: 2026-02-19
# Source: tests/payments/_setup/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

from playwright.sync_api import Page

from tests._functions.create_client.test import fn_create_client
from tests._functions.login.test import fn_login


def setup_payments(page: Page, context: dict) -> None:
    """
    Setup for payments category tests.

    Logs in and creates the client required by invoice picker flows.

    Credentials: from context (injected by runner from config.yaml target.auth). No fallbacks.

    Saves to context:
    - logged_in_user: The username that was logged in
    - created_client_id: ID of the client used by invoice flows
    - created_client_name: Full name used by invoice picker flows
    - created_client_email: Email of the invoice picker client
    - invoice_client_search_term: Search term used by invoice picker flows
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

    print("  Step 2: Creating invoice picker client...")
    fn_create_client(page, context, first_name="Appt", last_name="TestClient")
    context["invoice_client_search_term"] = context["created_client_name"]

    print("  Payments setup complete - user is logged in")
