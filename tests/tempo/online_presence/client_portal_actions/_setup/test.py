"""Setup for the client_portal_actions subcategory (isolated account).

Mirrors the legacy client-portal-actions.feature Background: log in to the
isolated account and create the verification client via the Platform API. The
client's portal token opens the client portal livesite as that client, which is
how the test verifies which actions the portal displays.
"""

import time

from playwright.sync_api import Page

from tests import account_api
from tests._functions.login.test import fn_login


def setup_client_portal_actions(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    seq = int(time.time())
    email = f"test+{seq}@vmeetme.com"
    print(f"  Setup Step 2: Create verification client via API ({email})")
    client = account_api.create_client(context, first_name="first", last_name="cpa", email=email)

    context["cpa"] = {
        "client_id": client["id"],
        "email": email,
        "portal_token": client["token"],
    }
    print(f"  [OK] setup complete - client {email} (portal token captured)")
