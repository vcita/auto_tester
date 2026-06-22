"""Setup for the Settings category.

Sets the business country to Israel (so the business-info page renders a known
country code) then logs in. Mirrors the legacy business_info_page Background
(account created with country_name=Israel + login).
"""

from playwright.sync_api import Page

from tests.account_api import update_business_country, wait_for_business_country
from tests._functions.login.test import fn_login


def setup_settings(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("username and password are missing from context")

    print("  Step 1: Setting business country to Israel...")
    update_business_country(context, "Israel")
    # Read the country back before logging in so the business-info page never loads
    # against a stale (not-yet-persisted) country value.
    wait_for_business_country(context, "Israel")

    print("  Step 2: Logging in...")
    fn_login(page, context, username=username, password=password)
    print(f"  [OK] settings setup complete - logged in as {context.get('logged_in_user')}")
