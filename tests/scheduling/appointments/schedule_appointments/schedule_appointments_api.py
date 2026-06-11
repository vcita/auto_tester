"""API setup + read-backs for the schedule_appointments migration (VCITA2-14025).

Mirrors the legacy scheduling-appointments.feature Background and the per-scenario API
prerequisites:
- `user creates new service via API`     -> create_appointment_service
- `user creates staff via Platform API`  -> create_staff
- `user creates new client via API`      -> create_client_with_readback
- `user updates settings via API` (arrival_window_value) -> set_arrival_window_setting
- `client gets an email where text includes` -> get_client_emails (automation message content API)

Thin wrappers over the shared, proven account_api primitives; booking read-backs reuse the
legacy appointments endpoint so a UI-created meeting can be opened by id.
"""

from __future__ import annotations

import time

import requests

from tests.account_api import (
    account_request,
    admin_headers,
    create_client,
    create_platform_staff_via_api,
    create_service_via_api,
    first_staff_uid,
    pivot_uid,
    resolve_api_base_url,
)

EMAIL_REQUEST_TIMEOUT = 20


def get_owner_staff(context: dict) -> dict:
    """Return the account owner staff {uid, display_name}. Call before creating extra staff."""
    response = account_request(
        context, "GET", f"/platform/v1/businesses/{pivot_uid(context)}/staffs?status=all"
    )
    staffs = response.get("data", {}).get("staff", [])
    if not staffs:
        raise ValueError("No staff returned for the owner lookup")
    owner = staffs[0]
    uid = owner.get("id") or owner.get("uid")
    context["account_first_staff_uid"] = uid
    return {"uid": uid, "display_name": owner.get("display_name") or owner.get("full_name")}


def create_staff(context: dict, name: str, email: str, role: str = "user") -> dict:
    """Create a Platform staff member (GET read-back inside the shared helper)."""
    return create_platform_staff_via_api(context, name, email, role)


def create_client_with_readback(context: dict, first_name: str, last_name: str, email: str) -> dict:
    client = create_client(context, first_name, last_name, email)
    _verify_client_persisted(context, email)
    return client


def _verify_client_persisted(context: dict, email: str) -> None:
    response = account_request(
        context,
        "GET",
        f"/platform/v1/clients?business_id={pivot_uid(context)}&search_by=email&search_value={email}",
    )
    clients = (response.get("data") or {}).get("clients") or response.get("clients") or []
    for client in clients:
        if (client.get("email") or "").lower() == email.lower():
            return
    raise AssertionError(f"Client {email!r} not found in clients read-back")


def create_appointment_service(context: dict, name: str, staff_uids: list[str]) -> dict:
    """Create a free (no-fee) appointment service assigned to ``staff_uids``."""
    service = create_service_via_api(context, name, staff_uids=staff_uids, charge_type="free")
    _verify_service_persisted(context, service["id"], name)
    return service


def _verify_service_persisted(context: dict, service_id: str, name: str) -> None:
    response = account_request(
        context, "GET", f"/platform/v1/services?business_id={pivot_uid(context)}"
    )
    services = (response.get("data") or {}).get("services") or response.get("services") or []
    for service in services:
        if (service.get("id") or service.get("uid")) == service_id:
            return
    raise AssertionError(f"Service {name!r} ({service_id}) not found in services read-back")


def set_account_arrival_window(context: dict, minutes: int) -> None:
    """Set the business-wide arrival-window value (legacy Background `update_settings`)."""
    account_request(context, "PUT", "/v2/settings", json={"arrival_window_value": minutes})


def set_service_arrival_window(context: dict, service_id: str, minutes: int) -> None:
    """Override a service's arrival window (legacy `edit_service` arrival_window)."""
    account_request(
        context,
        "PUT",
        f"/v2/settings/services/{service_id}",
        json={"arrival_window_override": True, "arrival_window_value": minutes},
    )


def list_appointment_ids(context: dict) -> set[str]:
    """Return the ids of all business appointments (snapshot before/after a UI schedule)."""
    response = account_request(
        context,
        "GET",
        f"/platform/v1/scheduling/appointments?business_id={pivot_uid(context)}",
    )
    appointments = (response.get("data") or {}).get("appointments") or []
    return {str(a.get("id")) for a in appointments if a.get("id") is not None}


def _directory_token(context: dict) -> str:
    """Mint a directory-scoped token (admin auth) to read the automation message inbox.

    The `/infra/automation/message/content` endpoint is directory-scoped (legacy `directory_api`,
    `Token <directory_token>`), so the account Bearer token is rejected. Mirrors card_on_file_api.
    """
    cached = context.get("_schedule_appts_dir_token")
    if cached:
        return cached
    directory_id = context.get("directory_id")
    if not directory_id:
        raise ValueError("directory_id is missing from context; cannot read the message inbox")
    response = requests.post(
        f"{resolve_api_base_url(context)}/platform/v1/tokens",
        json={"directory_id": str(directory_id)},
        headers=admin_headers(),
        timeout=EMAIL_REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    payload = response.json()
    token = (payload.get("data") or {}).get("token") or payload.get("token")
    if not token:
        raise ValueError(f"Could not mint a directory token from /platform/v1/tokens: {payload}")
    context["_schedule_appts_dir_token"] = token
    return token


def get_client_emails(context: dict) -> list[dict]:
    """Return automation message content for the business (legacy api/email.js _getPivotEmails).

    GET /infra/automation/message/content?business_uid=<pivot> (directory token) ->
    [{subject, text_part, ...}].
    """
    response = requests.get(
        f"{resolve_api_base_url(context)}/infra/automation/message/content",
        params={"business_uid": pivot_uid(context)},
        headers={"Authorization": f"Token {_directory_token(context)}"},
        timeout=EMAIL_REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    body = response.json()
    if isinstance(body, dict):
        return body.get("data") or body.get("messages") or []
    return body or []


def wait_for_client_email_texts(context: dict, texts: list[str], *, timeout_s: int = 90) -> dict:
    """Poll the automation email content until one email contains every text in ``texts``.

    Transient network errors (the integration API occasionally read-times-out) are swallowed and
    retried within the deadline so an infra blip does not fail the assertion.
    """
    deadline = time.time() + timeout_s
    seen_subjects: list[str] = []
    while time.time() < deadline:
        try:
            emails = get_client_emails(context)
        except requests.RequestException:
            time.sleep(3)
            continue
        for email in emails:
            body = email.get("text_part") or email.get("body") or ""
            if all(text in body for text in texts):
                return email
            seen_subjects.append(email.get("subject") or "")
        time.sleep(3)
    raise AssertionError(
        f"No email containing all of {texts!r} within {timeout_s}s; saw subjects {seen_subjects[-10:]}"
    )


__all__ = [
    "get_owner_staff",
    "create_staff",
    "create_client_with_readback",
    "create_appointment_service",
    "set_account_arrival_window",
    "set_service_arrival_window",
    "list_appointment_ids",
    "get_client_emails",
    "wait_for_client_email_texts",
    "first_staff_uid",
]
