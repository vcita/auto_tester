"""API setup for the events-list migration (VCITA2-13949).

Mirrors the legacy events-list.feature Background `user creates new service via API`
for two EVENT services with different payment settings:
- r2p_event: "require to pay"  -> charge_type paid_force
- daf_event: "display a fee"   -> charge_type paid_non_secured

The legacy service-creation endpoint is reused (POST /v2/settings/services via
``tests/account_api``), and persistence is confirmed with an independent GET
read-back (GET /platform/v1/services) before the UI relies on the service.
"""

from __future__ import annotations

from tests.account_api import (
    account_request,
    first_staff_uid,
    last_category_uid,
    pivot_uid,
)

EVENT_DURATION_MINUTES = 60
EVENT_MAX_ATTENDANCE = 2

# payment_setting -> charge_type (mirrors automation-js api/service._setPaymentType)
_CHARGE_TYPE_BY_PAYMENT_SETTING = {
    "require to pay": "paid_force",
    "suggest to pay": "paid",
    "display a fee": "paid_non_secured",
    "display free": "free",
    "display for a fee": "discuss",
}


def charge_type_for(payment_setting: str) -> str:
    try:
        return _CHARGE_TYPE_BY_PAYMENT_SETTING[payment_setting]
    except KeyError as exc:
        raise ValueError(f"Unknown payment_setting: {payment_setting!r}") from exc


def create_event_service(context: dict, name: str, payment_setting: str, price: str | int) -> dict:
    """Create an event service via API and verify it persists with a GET read-back.

    Mirrors legacy api/service.create_service with service_type=event and the given
    payment_setting. Returns {id, name, charge_type, price}.
    """
    charge_type = charge_type_for(payment_setting)
    payload = {
        "category": {"uid": last_category_uid(context)},
        "staff_data": [{"uid": first_staff_uid(context), "enabled": True}],
        "name": name,
        "service_type": "event",
        "currency": "USD",
        "duration": EVENT_DURATION_MINUTES,
        "interaction_type": "business_location",
        "meeting_interaction_details": "TLV",
        "charge_type": charge_type,
        "price": str(price),
        "display": "true",
        "max_attendance": EVENT_MAX_ATTENDANCE,
        "tax_uids": [],
    }
    response = account_request(context, "POST", "/v2/settings/services", json=payload)
    service = response.get("data") or response
    service_id = service.get("id") or service.get("uid")
    if not service_id:
        raise ValueError(f"Event service API response had no id: {response}")

    _verify_service_persisted(context, service_id, name)
    return {
        "id": service_id,
        "name": service.get("name") or name,
        "charge_type": charge_type,
        "price": str(price),
    }


def _verify_service_persisted(context: dict, service_id: str, name: str) -> None:
    """Independent GET read-back: a 200 on POST can silently drop fields, so confirm
    the service is actually listed before the UI relies on it (legacy get_services)."""
    response = account_request(
        context, "GET", f"/platform/v1/services?business_id={pivot_uid(context)}"
    )
    services = (response.get("data") or {}).get("services") or response.get("services") or []
    for service in services:
        if (service.get("id") or service.get("uid")) == service_id:
            return
    raise AssertionError(
        f"Event service {name!r} ({service_id}) not found in services read-back; "
        f"got {[s.get('name') for s in services]}"
    )
