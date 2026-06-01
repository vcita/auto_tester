"""API helpers for the card_on_file subcategory.

Provisions the prerequisite the legacy card-on-file.feature creates `via API`
(a client) and verifies the confirmation email the request triggers. The feature
under test (sending the card-on-file request) stays in the UI; only the client
and the email check are done through the API.

The email is read from the automation message inbox
(`GET /infra/automation/message/content?business_uid=<pivot_uid>`), the same
endpoint the legacy `client gets email with subject` step polls. That endpoint is
directory-scoped, so it is authenticated with a directory token (minted from the
directory id via `POST /platform/v1/tokens` with the admin token), mirroring the
legacy `directory_api` auth.
"""

from __future__ import annotations

import time

import requests

from tests.account_api import admin_headers, api_base, account_token

REQUEST_TIMEOUT = 20
EMAIL_POLL_SECONDS = 60
EMAIL_POLL_INTERVAL = 2


def _directory_token(context: dict) -> str:
    directory_id = context.get("directory_id")
    if not directory_id:
        raise ValueError("directory_id is missing from context; cannot read the message inbox")
    response = requests.post(
        f"{api_base(context)}/platform/v1/tokens",
        json={"directory_id": str(directory_id)},
        headers=admin_headers(),
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    payload = response.json()
    token = (payload.get("data") or {}).get("token") or payload.get("token")
    if not token:
        raise ValueError(f"Could not mint a directory token from /platform/v1/tokens: {payload}")
    return token


def create_client(context: dict, first_name: str, last_name: str, email: str) -> dict:
    """Create a client and return its id and full name."""
    response = requests.post(
        f"{api_base(context)}/platform/v1/clients",
        json={
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "source_name": "automation",
        },
        headers={"Authorization": f"Bearer {account_token(context)}"},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    payload = response.json().get("data") or response.json()
    client = payload.get("client") or payload
    client_id = client.get("id") or client.get("uid")
    if not client_id:
        raise ValueError(f"Client API response did not include an id: {payload}")
    client["id"] = client_id
    client["full_name"] = f"{first_name} {last_name}"
    return client


def enable_credit_card(context: dict) -> None:
    """Enable credit-card checkout via the payment-settings API.

    The redesigned add-payment-method dialog only offers the "Request card on file"
    segment when credit-card payments are enabled for the business; this mirrors the
    legacy `allow_credit_card` account state.
    """
    requests.post(
        f"{api_base(context)}/platform/v1/payment/settings",
        json={"payment_settings": {"allow_credit_card": True}},
        headers={"Authorization": f"Bearer {account_token(context)}"},
        timeout=REQUEST_TIMEOUT,
    ).raise_for_status()


def _pivot_uid(context: dict) -> str:
    auto_account = context.get("auto_account") or {}
    pivot_uid = auto_account.get("pivot_uid") or auto_account.get("business_id")
    if not pivot_uid:
        raise ValueError("auto_account pivot_uid is missing from context")
    return pivot_uid


def wait_for_email_subject(context: dict, subject: str) -> dict:
    """Poll the account's automation inbox until an email with `subject` arrives.

    Account-scoped messages can lag the UI action by several seconds, so this is a
    backend eventual-consistency poll (not a UI wait); it raises if the email never
    arrives within the budget.
    """
    url = f"{api_base(context)}/infra/automation/message/content"
    params = {"business_uid": _pivot_uid(context)}
    headers = {"Authorization": f"Token {_directory_token(context)}"}
    deadline = time.monotonic() + EMAIL_POLL_SECONDS
    last_subjects: list = []
    while time.monotonic() < deadline:
        response = requests.get(
            url, params=params, headers=headers, timeout=REQUEST_TIMEOUT
        )
        if response.ok:
            emails = response.json() or []
            last_subjects = [item.get("subject") for item in emails]
            match = next((item for item in emails if item.get("subject") == subject), None)
            if match is not None:
                return match
        time.sleep(EMAIL_POLL_INTERVAL)
    raise AssertionError(
        f"Email with subject '{subject}' not received within {EMAIL_POLL_SECONDS}s. "
        f"Inbox subjects seen: {last_subjects}"
    )
