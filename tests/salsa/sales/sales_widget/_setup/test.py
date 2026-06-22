"""Setup for the Sales Widget subcategory (isolated account).

Mirrors the legacy sales_widget.feature Background ("user creates automatic
account with FF new_dashboard"): enable the new_dashboard flag before login so the
dashboard renders the Sales widget, then log in to the fresh isolated account.
"""

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.salsa.sales.sales_widget.sales_widget_helpers import enable_new_dashboard


def setup_sales_widget(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Enable new_dashboard feature flag (before login)")
    enable_new_dashboard(context)

    print("  Setup Step 2: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    print("  [OK] setup complete - new_dashboard enabled, logged in")
