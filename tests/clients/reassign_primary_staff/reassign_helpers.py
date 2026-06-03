"""API setup + email-polling helpers for the Reassign Primary Staff migration.

Mirrors the API-setup primitives proven by ``recently_active_helpers.py`` (client,
service, appointment) and adds Platform staff creation plus a business email poll
(``/infra/automation/message/content``) that the legacy ``api/email.js`` used to
assert assignment-notification emails.
"""

import os
import time
from datetime import datetime, timedelta, timezone

import requests

from tests.account_api import admin_headers

REQUEST_TIMEOUT = 5
# Assignment emails are delivered asynchronously. Legacy retried ~30x. We poll with
# a per-request 5s timeout and a bounded total budget (documented exception to the
# 5s element cap, same class as the reviews async-email check) - no fixed sleeps.
EMAIL_POLL_BUDGET_SECONDS = 90
EMAIL_POLL_INTERVAL_SECONDS = 3
APPOINTMENT_LEAD_DAYS = 30


# --------------------------------------------------------------------------- #
# API setup
# --------------------------------------------------------------------------- #
def create_platform_staff_via_api(context: dict, name: str, email: str, role: str = "user") -> dict:
    response = _account_request(
        context,
        "POST",
        f"/platform/v1/businesses/{_get_pivot_uid(context)}/staffs",
        json={"staff": {"display_name": name, "email": email, "role": role.lower()}},
    )
    payload = response.get("data") or response
    staff = (payload.get("staff") or [payload])
    staff = staff[0] if isinstance(staff, list) else staff
    staff.setdefault("display_name", name)
    staff.setdefault("email", email)
    return staff


def create_client_via_api(context: dict, first_name: str, last_name: str, email: str) -> dict:
    response = _account_request(
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


def create_service_via_api(context: dict, service_name: str) -> dict:
    payload = {
        "category": {"uid": _get_last_category_uid(context)},
        "staff_data": [{"uid": _get_first_staff_uid(context), "enabled": True}],
        "name": service_name,
        "service_type": "appointment",
        "currency": "USD",
        "duration": 60,
        "interaction_type": "business_location",
        "meeting_interaction_details": "TLV",
        "charge_type": "free",
        "display": "true",
        "max_attendance": 2,
    }
    response = _account_request(context, "POST", "/v2/settings/services", json=payload)
    service = response.get("data") or response
    service_id = service.get("id") or service.get("uid")
    if not service_id:
        raise ValueError(f"Service API response did not include an id: {response}")
    return {"id": service_id, "name": service.get("name") or service_name}


def create_appointment_via_api(context: dict, service: dict, client: dict) -> dict:
    """Schedule an appointment assigned to the account owner (NOT Staff B).

    The reassign-with-checkbox UI flow is what must move it to Staff B, so the
    initial assignee deliberately stays the owner/primary staff.
    """
    payload = {
        "business_id": _get_pivot_uid(context),
        "staff_id": _get_first_staff_uid(context),
        "start_time": _future_start_time(),
        "service_id": service["id"],
        "client_id": client["id"],
    }
    response = _account_request(context, "POST", "/business/scheduling/v1/bookings", json=payload)
    data = response.get("data") or response
    return data.get("booking") or data


# --------------------------------------------------------------------------- #
# Assignment email poll
# --------------------------------------------------------------------------- #
def get_business_email_by_subject(context: dict, subject: str) -> dict:
    """Poll the business automation mailbox until an email with ``subject`` exists.

    GET /infra/automation/message/content?business_uid=<pivot> with directory-token
    auth, mirroring legacy ``api/email.js``. Bounded by EMAIL_POLL_BUDGET_SECONDS.
    """
    base_url = _resolve_api_base_url(context)
    headers = {"Authorization": f"Token {_resolve_directory_token(context)}"}
    pivot_uid = _get_pivot_uid(context)
    path = f"/infra/automation/message/content?business_uid={pivot_uid}"

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
        f"Email with subject {subject!r} not found for business {pivot_uid} "
        f"within {EMAIL_POLL_BUDGET_SECONDS}s. Last seen subjects: {last_subjects}"
    )


# --------------------------------------------------------------------------- #
# Low-level request + context accessors (mirror recently_active_helpers)
# --------------------------------------------------------------------------- #
def _account_request(context: dict, method: str, path: str, **kwargs) -> dict:
    response = requests.request(
        method,
        f"{_resolve_api_base_url(context)}{path}",
        headers=_account_headers(context),
        timeout=REQUEST_TIMEOUT,
        **kwargs,
    )
    if not response.ok:
        raise requests.HTTPError(
            f"{response.status_code} {response.reason} for {path}: {response.text[:500]}",
            response=response,
        )
    return response.json() if response.text else {}


def _resolve_api_base_url(context: dict) -> str:
    api_base_url = context.get("api_base_url")
    if api_base_url:
        return api_base_url.rstrip("/")

    base_url = (context.get("base_url") or "").rstrip("/")
    if "meet2know.com" in base_url:
        return "https://api2.meet2know.com"
    if "vcita.com" in base_url:
        return "https://api.vcita.biz"
    if "app-" in base_url and ".external.int-eks.vchost.co" in base_url:
        return base_url.replace("https://app-", "https://core-", 1)

    raise ValueError("api_base_url is missing from context and could not be inferred")


def _account_headers(context: dict) -> dict:
    auto_account = context.get("auto_account") or {}
    token = auto_account.get("api_token") or auto_account.get("auth_token")
    if not token:
        raise ValueError("auto_account api_token is missing from context")
    return {"Authorization": f"Bearer {token}"}


def _get_pivot_uid(context: dict) -> str:
    auto_account = context.get("auto_account") or {}
    pivot_uid = auto_account.get("pivot_uid") or auto_account.get("business_id")
    if not pivot_uid:
        raise ValueError("auto_account pivot_uid is missing from context")
    return pivot_uid


def _get_last_category_uid(context: dict) -> str:
    response = _account_request(
        context, "GET", f"/platform/v1/categories?business_id={_get_pivot_uid(context)}"
    )
    categories = response.get("data", {}).get("categories", [])
    if not categories:
        raise ValueError("No service categories returned for auto account")
    return categories[-1]["id"]


def _get_first_staff_uid(context: dict) -> str:
    cached = context.get("reassign_owner_staff_uid")
    if cached:
        return cached
    response = _account_request(
        context, "GET", f"/platform/v1/businesses/{_get_pivot_uid(context)}/staffs?status=all"
    )
    staffs = response.get("data", {}).get("staff", [])
    if not staffs:
        raise ValueError("No staff returned for auto account")
    staff_uid = staffs[0].get("id") or staffs[0].get("uid")
    context["reassign_owner_staff_uid"] = staff_uid
    return staff_uid


def _resolve_directory_token(context: dict) -> str:
    """Directory token for the automation mailbox endpoint.

    Prefer an explicit ``VCITA_DIRECTORY_TOKEN``; otherwise generate/reuse one from
    ``directory_id`` + admin token (same flow proven by VCITA2-13777). Kept local to
    avoid coupling the clients category to the scheduling package.
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

    base_url = _resolve_api_base_url(context)
    headers = admin_headers()
    existing = requests.get(
        f"{base_url}/platform/v1/tokens",
        params={"directory_id": directory_id},
        headers=headers,
        timeout=REQUEST_TIMEOUT,
    )
    if existing.ok and existing.text:
        tokens = (existing.json().get("data") or {}).get("tokens") or []
        if tokens and tokens[0].get("token"):
            return tokens[0]["token"]

    created = requests.post(
        f"{base_url}/platform/v1/tokens",
        json={"directory_id": directory_id},
        headers=headers,
        timeout=REQUEST_TIMEOUT,
    )
    created.raise_for_status()
    body = created.json()
    token = (body.get("data") or {}).get("token") or body.get("token")
    if not token:
        raise ValueError(f"Directory token generation returned no token: {body}")
    return token


def _future_start_time() -> str:
    start_time = datetime.now(timezone.utc) + timedelta(days=APPOINTMENT_LEAD_DAYS)
    start_time = start_time.replace(minute=0, second=0, microsecond=0)
    return start_time.isoformat().replace("+00:00", "Z")
