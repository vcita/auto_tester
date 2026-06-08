# Matters Management Setup
# Migrated from automation-js/features/steps/matters-management.feature (VCITA2-13952)
# Source: tests/clients/matters_management/_setup/script.md

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import create_client


def setup_matters_management(page: Page, context: dict) -> None:
    """Log in to the isolated account and create the two background contacts.

    Mirrors the legacy Background:
      Given user logged in to automatic account
      And user creates new client via API (matter client, contact client)
    """
    username = context.get("username")
    password = context.get("password")
    if not username or not password:
        raise ValueError(
            "username/password not in context. Isolated account must be created by the runner."
        )

    print("  Step 1: Logging in to isolated account...")
    fn_login(page, context, username=username, password=password)

    ts = int(time.time())
    matter_email = f"matter+{ts}@vmeetme.com"
    contact_email = f"contact+{ts}@vmeetme.com"

    print("  Step 2: Creating 'matter client' contact via API...")
    matter_c = create_client(context, "matter", "client", matter_email)
    print("  Step 3: Creating 'contact client' contact via API...")
    contact_c = create_client(context, "contact", "client", contact_email)

    context["matter_client_id"] = matter_c["id"]
    context["matter_client_name"] = matter_c["full_name"]
    context["matter_client_email"] = matter_c.get("email") or matter_email
    context["contact_client_id"] = contact_c["id"]
    context["contact_client_name"] = contact_c["full_name"]
    context["contact_client_email"] = contact_c.get("email") or contact_email

    print(
        f"  Setup complete - matter_client={context['matter_client_id']} "
        f"contact_client={context['contact_client_id']}"
    )
