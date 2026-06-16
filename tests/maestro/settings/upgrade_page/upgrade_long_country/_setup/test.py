"""Setup for the Upgrade Long Country scenario.

The isolated account is created with country "Bolivia, Plurinational State of" and
the automation feature flags (incl. hide_register_wizard). This blocks the Recurly
trust-seal script and logs in.
"""

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.maestro.settings.upgrade_page.upgrade_helpers import block_trust_seal


def setup_upgrade_long_country(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("username and password are missing from context")

    block_trust_seal(page)
    print("  Step: Log in to isolated Trial account (long country name)")
    fn_login(page, context, username=username, password=password)
    print(f"  [OK] logged in as {context.get('logged_in_user')}")
