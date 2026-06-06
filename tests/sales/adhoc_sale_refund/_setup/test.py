"""Setup for the ad-hoc sale + refund subcategory (isolated account).

Mirrors the legacy sales.feature Background: log in to the isolated account and
create the client "first last" via API. The client is created with the same email
the make-payment form uses, so the resulting sale is attributed to "first last".
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import create_client

CLIENT_FIRST_NAME = "first"
CLIENT_LAST_NAME = "last"


def setup_adhoc_sale_refund(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 2: Create client 'first last' via API")
    email = f"test+{int(time.time() * 1000)}@vmeetme.com"
    client = create_client(context, CLIENT_FIRST_NAME, CLIENT_LAST_NAME, email)
    context["adhoc_client_name"] = client["full_name"]
    context["adhoc_client_email"] = email
    context["adhoc_client_first_name"] = CLIENT_FIRST_NAME

    print(f"  [OK] setup complete - client '{client['full_name']}' ({email}) ready")
