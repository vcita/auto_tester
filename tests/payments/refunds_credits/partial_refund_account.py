"""Account preparation helpers for the partial-refund subcategories.

Handles optional point_of_sale denial (before login), login, and client creation.
"""

import os
import time

import requests
from playwright.sync_api import Page

from tests._functions.login.test import fn_login

REQUEST_TIMEOUT = 30
CLIENT_FIRST_NAME = "Torry"
CLIENT_LAST_NAME = "Deposi"


def _admin_headers() -> dict:
    admin_token = os.environ.get("VCITA_ADMIN_TOKEN")
    if not admin_token:
        raise ValueError("VCITA_ADMIN_TOKEN is not set; cannot manage feature flags")
    return {"Authorization": f"Admin {admin_token}"}


def deny_point_of_sale(context: dict) -> None:
    """Deny point_of_sale before login so Quick Actions exposes the legacy Record payment dialog."""
    user_id = (context.get("auto_account") or {}).get("user_id")
    api_base_url = context.get("api_base_url")
    if not (user_id and api_base_url):
        raise ValueError("user_id or api_base_url missing for point_of_sale denial")

    api = api_base_url.rstrip("/")
    headers = _admin_headers()
    response = requests.post(
        f"{api}/admin/feature_flags/{user_id}/blacklist_user_features",
        json={"features": "point_of_sale"},
        headers=headers,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    requests.get(
        f"{api}/infra/automation/reset_features_table_cache",
        headers=headers,
        timeout=REQUEST_TIMEOUT,
    )


def create_client(context: dict) -> None:
    auto_account = context.get("auto_account") or {}
    token = auto_account.get("api_token") or auto_account.get("auth_token")
    if not token:
        raise ValueError("auto_account api_token is missing from context")

    timestamp = int(time.time())
    response = requests.post(
        f"{context['api_base_url'].rstrip('/')}/platform/v1/clients",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": CLIENT_FIRST_NAME,
            "last_name": CLIENT_LAST_NAME,
            "email": f"test+{timestamp}@vmeetme.com",
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
