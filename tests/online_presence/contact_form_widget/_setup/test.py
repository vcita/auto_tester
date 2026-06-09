"""Setup for the contact_form_widget subcategory.

Mirrors the legacy contact-form-widget.feature prerequisites: log in to the
isolated account and create the target client via API. The same client is later
marked as spam (UI) and its conversation is asserted empty after the spam
submission, so it is stored in context.
"""

import time

from playwright.sync_api import Page

from tests import account_api
from tests._functions.login.test import fn_login


def setup_contact_form_widget(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    seq = int(time.time())
    first, last = "first", "last"
    email = f"test+{seq}@vmeetme.com"
    client = account_api.create_client(context, first_name=first, last_name=last, email=email)
    print(f"  [OK] Created target client via API: {email}")

    context["cfw"] = {
        "seq": seq,
        "first_name": first,
        "last_name": last,
        "email": email,
        "full_name": f"{first} {last}",
        "client_id": client["id"],
        "message": "hello",
    }
