"""API setup + read-backs for the multistaff migration (VCITA2-13950).

Mirrors the legacy multistaff.feature Background:
- `user creates staff via Platform API`  -> create_staff (POST staffs, GET read-back)
- `user creates new client via API`      -> create_client_with_readback
- `user creates new service via API`     -> create_appointment_service (POST service, GET read-back)

Staff creation and the SSO staff switch reuse the shared, proven helpers
(``account_api.create_platform_staff_via_api`` already resolves via a GET staff-list
read-back; ``calendar_helpers.switch_logged_in_staff`` performs the SSO login). Booking
look-up reuses the legacy appointments endpoint so the UI-created meeting can be opened by
id (legacy ``addBookingToContext``).
"""

from __future__ import annotations

from tests.account_api import (
    account_request,
    create_client,
    create_platform_staff_via_api,
    create_service_via_api,
    first_staff_uid,
    pivot_uid,
)


def get_owner_staff(context: dict) -> dict:
    """Return the account owner staff {uid, display_name}.

    Call BEFORE creating extra staff so the owner is unambiguously the first staff. The
    owner display name is scenario 2's expected ``assigned_staff`` (the legacy
    "Automation test business" value, which is account-generated on a fresh account).
    """
    response = account_request(
        context, "GET", f"/platform/v1/businesses/{pivot_uid(context)}/staffs?status=all"
    )
    staffs = response.get("data", {}).get("staff", [])
    if not staffs:
        raise ValueError("No staff returned for the auto account owner lookup")
    owner = staffs[0]
    uid = owner.get("id") or owner.get("uid")
    context["account_first_staff_uid"] = uid  # cache for first_staff_uid()
    return {"uid": uid, "display_name": owner.get("display_name") or owner.get("full_name")}


def create_staff(context: dict, name: str, email: str, role: str) -> dict:
    """Create a Platform staff member (GET staff-list read-back inside the shared helper)."""
    return create_platform_staff_via_api(context, name, email, role)


def create_client_with_readback(context: dict, first_name: str, last_name: str, email: str) -> dict:
    """Create a client and confirm it persists with an independent GET read-back.

    A 200 on POST can still drop a record; the legacy flow relied on the client being
    listable, so confirm via GET /platform/v1/clients?search_by=email before the UI uses it.
    """
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
    raise AssertionError(
        f"Client {email!r} not found in clients read-back; got {[c.get('email') for c in clients]}"
    )


def create_appointment_service(context: dict, name: str, staff_uids: list[str]) -> dict:
    """Create a 'require to pay' appointment service assigned to ``staff_uids``.

    Mirrors legacy `user creates new service via API` (f2f_other / business_location,
    require to pay, price 1). Confirmed with a GET services read-back before the UI uses it.
    """
    service = create_service_via_api(
        context, name, staff_uids=staff_uids, charge_type="paid_force", price="1"
    )
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
    raise AssertionError(
        f"Service {name!r} ({service_id}) not found in services read-back; "
        f"got {[s.get('name') for s in services]}"
    )


def list_appointment_ids(context: dict) -> set[str]:
    """Return the ids of all business appointments (legacy get_appointments).

    Used to snapshot before/after a UI schedule so the newly created meeting can be
    resolved unambiguously (the fresh account accumulates appointments across the two tests).
    """
    response = account_request(
        context,
        "GET",
        f"/platform/v1/scheduling/appointments?business_id={pivot_uid(context)}",
    )
    appointments = (response.get("data") or {}).get("appointments") or []
    return {str(a.get("id")) for a in appointments if a.get("id") is not None}


__all__ = [
    "get_owner_staff",
    "create_staff",
    "create_client_with_readback",
    "create_appointment_service",
    "list_appointment_ids",
    "first_staff_uid",
]
