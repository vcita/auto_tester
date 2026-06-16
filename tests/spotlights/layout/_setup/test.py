"""Setup for the Layout category.

Enables the `new_dashboard` feature flag (so `/app/dashboard` renders the POV new
dashboard layer) then logs in. Mirrors the legacy `icons.feature` Background.
"""

from playwright.sync_api import Page

from tests.account_api import enable_features
from tests._functions.login.test import fn_login


def setup_layout(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("username and password are missing from context")

    print("  Step 1: Enabling new_dashboard feature flag...")
    enable_features(context, "new_dashboard")

    print("  Step 2: Logging in...")
    fn_login(page, context, username=username, password=password)
    print(f"  [OK] layout setup complete - logged in as {context.get('logged_in_user')}")
