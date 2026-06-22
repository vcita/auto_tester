"""Setup for the Upgrade In Frontage scenario.

Blocks the Recurly trust-seal script (so the later checkout page mounts its hosted
card fields) and logs in to the isolated Trial account.
"""

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.maestro.settings.upgrade_page.upgrade_helpers import block_trust_seal


def setup_upgrade_in_frontage(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("username and password are missing from context")

    block_trust_seal(page)
    print("  Step: Log in to isolated Trial account")
    fn_login(page, context, username=username, password=password)
    print(f"  [OK] logged in as {context.get('logged_in_user')}")
