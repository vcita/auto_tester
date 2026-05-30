"""Account preparation helpers for the partial-refund subcategories.

Handles optional point_of_sale denial (before login), login, and client creation.
"""

import uuid

import requests
from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import REQUEST_TIMEOUT, account_token, api_base, deny_features

CLIENT_FIRST_NAME = "Torry"
CLIENT_LAST_NAME = "Deposi"


def deny_point_of_sale(context: dict) -> None:
    """Deny point_of_sale before login so Quick Actions exposes the legacy Record payment dialog."""
    deny_features(context, "point_of_sale")


def create_client(context: dict) -> None:
    unique_suffix = uuid.uuid4().hex[:10]
    response = requests.post(
        f"{api_base(context)}/platform/v1/clients",
        headers={"Authorization": f"Bearer {account_token(context)}"},
        json={
            "first_name": CLIENT_FIRST_NAME,
            "last_name": CLIENT_LAST_NAME,
            "email": f"test+{unique_suffix}@vmeetme.com",
            "source_name": "automation",
        },
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    payload = response.json().get("data") or response.json()
    client = payload.get("client") or payload
    client_id = client.get("id") or client.get("uid")
    if not client_id:
        raise ValueError(f"Client API response did not include an id: {response.text[:300]}")

    context["created_client_id"] = client_id
    context["created_client_name"] = f"{CLIENT_FIRST_NAME} {CLIENT_LAST_NAME}"
    context["created_client_email"] = client.get("email")


def prepare_account(page: Page, context: dict, deny_pos: bool = False) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    if deny_pos:
        print("  Step: Deny point_of_sale (before login)")
        deny_point_of_sale(context)

    print("  Step: Log in to isolated account")
    fn_login(page, context, username=username, password=password)
    print("  Step: Create client via API")
    create_client(context)
    print(f"  Setup complete - client {context['created_client_name']} ready")
