"""Setup for matter_deletion: log in to the isolated account and create the contact.

Mirrors the legacy Background:
  Given user logged in to automatic account
  And user creates new client via API (contact / last)
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import create_client


def setup_matter_deletion(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Step 1: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    email = f"contact+{int(time.time())}@vmeetme.com"
    print("  Step 2: Create 'contact last' contact via API")
    contact = create_client(context, "contact", "last", email)

    context["contact_id"] = contact["id"]
    context["contact_name"] = contact["full_name"]
    context["contact_email"] = contact.get("email") or email
    print(f"  Setup complete - contact={context['contact_id']} ({context['contact_email']})")
