"""Setup for the Deposits subcategory.

Mirrors the legacy deposits.feature Background: log in to the isolated account and
create the client "Torry Deposi". The client is created with its client-portal JWT
token so the client-portal scenarios (sign+pay, offline deposit) can open the portal
as that client.

Feature-flag state (point_of_sale) is NOT set here: the invoice scenarios manage it
themselves (quick-actions path denies POS, POS path enables it) so the two are
order-independent on the shared account.
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import create_client

CLIENT_FIRST_NAME = "Torry"
CLIENT_LAST_NAME = "Deposi"


def setup_deposits(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 2: Create client 'Torry Deposi' via API (with portal token)")
    stamp = int(time.time() * 1000)
    email = f"test+{stamp}@vmeetme.com"
    client = create_client(context, CLIENT_FIRST_NAME, CLIENT_LAST_NAME, email)
    context["deposit_client"] = client
    context["deposit_client_id"] = client["id"]
    context["deposit_client_name"] = client["full_name"]
    context["deposit_client_email"] = email
    context["deposit_client_token"] = client["token"]

    print(f"  [OK] deposits setup complete - client '{client['full_name']}' ready")
