"""Reassign-specific API setup + email-polling helpers.

The generic account-scoped primitives (request wrapper, staff/service/appointment
builders) live in ``tests/account_api`` and are reused here. This module only adds
what is unique to the reassign test: Platform staff creation, client creation, a
directory-token resolver, and the business email poll
(``/infra/automation/message/content``) that the legacy ``api/email.js`` used.
"""

import os
import time

import requests

from tests.account_api import (
    account_request,
    admin_headers,
    create_appointment_via_api,
    create_platform_staff_via_api,
    create_service_via_api,
    first_staff_uid,
    pivot_uid,
    resolve_api_base_url,
)

__all__ = [
    "create_appointment_via_api",
    "create_client_via_api",
    "create_platform_staff_via_api",
    "create_service_via_api",
    "first_staff_uid",
    "get_business_email_by_subject",
]

REQUEST_TIMEOUT = 5
# Assignment emails are delivered asynchronously. We poll with a per-request 5s
# timeout and a bounded total budget (a documented exception to the 5s element
# cap, same class as the reviews async-email check). The interval below is a poll
# cadence, not a wait-for-action sleep.
EMAIL_POLL_BUDGET_SECONDS = 90
EMAIL_POLL_INTERVAL_SECONDS = 3


def create_client_via_api(context: dict, first_name: str, last_name: str, email: str) -> dict:
    response = account_request(
        context,
        "POST",
        "/platform/v1/clients",
        json={
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "source_name": "automation",
        },
    )
    payload = response.get("data") or response
    client = payload.get("client") or payload
    client_id = client.get("id") or client.get("uid")
    if not client_id:
        raise ValueError(f"Client API response did not include an id: {response}")
    return {
        "id": client_id,
        "name": f"{first_name} {last_name}".strip(),
        "email": client.get("email") or email,
    }


def get_business_email_by_subject(context: dict, subject: str) -> dict:
    """Poll the business automation mailbox until an email with ``subject`` exists.

    GET /infra/automation/message/content?business_uid=<pivot> with directory-token
    auth, mirroring legacy ``api/email.js``. Bounded by EMAIL_POLL_BUDGET_SECONDS.
    """
    base_url = resolve_api_base_url(context)
    headers = {"Authorization": f"Token {_resolve_directory_token(context)}"}
    business_uid = pivot_uid(context)
    path = f"/infra/automation/message/content?business_uid={business_uid}"

    deadline = time.monotonic() + EMAIL_POLL_BUDGET_SECONDS
    last_subjects: list[str] = []
    while time.monotonic() < deadline:
        try:
            response = requests.get(f"{base_url}{path}", headers=headers, timeout=REQUEST_TIMEOUT)
            if response.ok:
                emails = response.json() or []
                if isinstance(emails, dict):
                    emails = emails.get("data") or emails.get("emails") or []
                last_subjects = [e.get("subject") for e in emails if isinstance(e, dict)]
                for email in emails:
                    if isinstance(email, dict) and email.get("subject") == subject:
                        return email
        except (requests.ReadTimeout, requests.ConnectionError):
            pass
        time.sleep(EMAIL_POLL_INTERVAL_SECONDS)

    raise AssertionError(
        f"Email with subject {subject!r} not found for business {business_uid} "
        f"within {EMAIL_POLL_BUDGET_SECONDS}s. Last seen subjects: {last_subjects}"
    )


def _resolve_directory_token(context: dict) -> str:
    """Directory token for the automation mailbox endpoint.

    Prefer an explicit ``VCITA_DIRECTORY_TOKEN``; otherwise generate/reuse one from
    ``directory_id`` + admin token (same flow proven by VCITA2-13777).
    """
    env_token = os.environ.get("VCITA_DIRECTORY_TOKEN")
    if env_token:
        return env_token

    directory_id = context.get("directory_id") or os.environ.get("VCITA_DIRECTORY_ID")
    if not directory_id:
        raise ValueError(
            "Cannot resolve a directory token for the email check: set VCITA_DIRECTORY_TOKEN, "
            "or provide a directory_id (context/VCITA_DIRECTORY_ID) plus VCITA_ADMIN_TOKEN."
        )

    headers = admin_headers()
    existing = account_request(
        context, "GET", "/platform/v1/tokens", params={"directory_id": directory_id}, headers=headers
    )
    tokens = (existing.get("data") or {}).get("tokens") or []
    if tokens and tokens[0].get("token"):
        return tokens[0]["token"]

    created = account_request(
        context, "POST", "/platform/v1/tokens", json={"directory_id": directory_id}, headers=headers
    )
    token = (created.get("data") or {}).get("token") or created.get("token")
    if not token:
        raise ValueError(f"Directory token generation returned no token: {created}")
    return token
