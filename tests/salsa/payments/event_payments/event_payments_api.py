"""API setup for the event_payments migration (VCITA2-13856).

Mirrors the legacy event-payments.feature Background and the per-scenario API
seeding: create a "require to pay" event service, schedule an event instance, and
register clients as attendees. Reuses the shared account plumbing in
``tests/account_api`` (token/base url/staff/category resolution) and adds the
event-instance endpoints that account_api does not cover.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

from tests.account_api import (
    account_request,
    create_client,
    first_staff_uid,
    last_category_uid,
    pivot_uid,
)

EVENT_DURATION_MINUTES = 60
EVENT_MAX_ATTENDANCE = 2
EVENT_LEAD_DAYS = 20


def create_event_service(context: dict, name: str, price: str | int) -> dict:
    """Create a 'require to pay' (charge_type paid_force) event service via API.

    Mirrors legacy api/service.create_service with service_type=event and
    payment_setting "require to pay"."""
    payload = {
        "category": {"uid": last_category_uid(context)},
        "staff_data": [{"uid": first_staff_uid(context), "enabled": True}],
        "name": name,
        "service_type": "event",
        "currency": "USD",
        "duration": EVENT_DURATION_MINUTES,
        "interaction_type": "business_location",
        "meeting_interaction_details": "TLV",
        "charge_type": "paid_force",
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
    return {
        "id": service_id,
        "name": service.get("name") or name,
        "price": str(price),
        "duration": service.get("duration") or EVENT_DURATION_MINUTES,
        "interaction_type": service.get("interaction_type") or "business_location",
        "interaction_details": service.get("meeting_interaction_details") or "TLV",
        "max_attendance": service.get("max_attendance") or EVENT_MAX_ATTENDANCE,
    }


def schedule_event(context: dict, service: dict) -> dict:
    """Schedule an event instance for a service (POST /v2/event_instances).

    The event_instances endpoint treats a timezone-less start_time as the
    business-local wall-clock (see calendar_api.resolve_api_datetime), so a naive
    near-future datetime is sent as-is."""
    start_time = (datetime.now() + timedelta(days=EVENT_LEAD_DAYS)).replace(
        hour=10, minute=0, second=0, microsecond=0
    )
    end_time = start_time + timedelta(minutes=int(service.get("duration") or EVENT_DURATION_MINUTES))
    response = account_request(
        context,
        "POST",
        "/v2/event_instances",
        json={
            "title": service["name"],
            "event_service_id": service["id"],
            "interaction_type": service.get("interaction_type", "business_location"),
            "interaction_details": service.get("interaction_details", "TLV"),
            "max_attendance": service.get("max_attendance", EVENT_MAX_ATTENDANCE),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "charge_type": "paid_force",
            "price": service["price"],
            "currency": "USD",
            "staff_id": first_staff_uid(context),
            "duration": service.get("duration", EVENT_DURATION_MINUTES),
            "padding": 0,
            "display": True,
        },
    )
    event = response.get("data") or response
    event_uid = event.get("uid") or event.get("id")
    if not event_uid:
        raise ValueError(f"Event instance API response had no uid: {response}")
    return {"uid": event_uid, "name": service["name"]}


def register_clients_to_event(context: dict, event_uid: str, client_ids: list[str]) -> None:
    """Register attendees on an event (bulk_create), mirroring legacy register_clients_to_event."""
    account_request(
        context,
        "POST",
        f"/v2/event_instances/{event_uid}/event_attendances/bulk_create",
        json={
            "client_ids": client_ids,
            "invite_message": None,
            "applySeries": False,
            "apply_on_series": False,
        },
    )


def create_event_package(
    context: dict, *, name: str, service: dict, credits: int, price: str | int,
) -> dict:
    """Create a 'specific' package offering `service` for `credits` bookings.

    Mirrors legacy packages_api.create_package with parseCreatePackageTableAPI for a
    single specific service item."""
    item = {
        "services": [{
            "name": service["name"],
            "price": str(service["price"]),
            "currency": "USD",
            "id": service["id"],
        }],
        "total_bookings": credits,
    }
    response = account_request(context, "POST", "/platform/v1/payment/packages", json={
        "items": [item],
        "products": [],
        "discount_unit": "p",
        "online_payment_enabled": True,
        "expiration": 3,
        "expiration_unit": "m",
        "name": name,
        "description": "",
        "price": str(price),
        "id": None,
        "currency": "USD",
        "use_platform_api": True,
    })
    package = (response.get("data") or response).get("package") or response.get("data") or response
    package_id = package.get("id") or package.get("uid")
    if not package_id:
        raise ValueError(f"Package API response had no id: {response}")
    return {"id": package_id, "name": name, "price": str(price)}


def assign_package_to_client(
    context: dict, *, client_id: str, package_id: str, price: str | int,
) -> dict:
    """Assign a package to a client (mirrors legacy packages_api.assign_package)."""
    valid_from = (date.today() - timedelta(days=1)).isoformat()
    valid_until = (date.today() + timedelta(days=89)).isoformat()
    response = account_request(context, "POST", "/platform/v1/payment/client_packages", json={
        "client_id": client_id,
        "package_id": package_id,
        "price": str(price),
        "valid_from": valid_from,
        "valid_until": valid_until,
        "tax_uids": None,
        "use_platform_api": True,
    })
    return (response.get("data") or response).get("client_package") or response


def seed_event_package_redeem(
    context: dict, *, service_name: str, price: str | int,
    package_name: str, credits: int, package_price: str | int,
    first: str, last: str, email: str,
) -> dict:
    """Scenario-5 setup: event service + event + a client holding a package that
    offers the event, registered as the sole attendee (one order to redeem).

    Stores the seeded entities in context under ``event_payments``."""
    service = create_event_service(context, service_name, price)
    event = schedule_event(context, service)
    client = create_client(context, first, last, email)
    package = create_event_package(
        context, name=package_name, service=service, credits=credits, price=package_price
    )
    assign_package_to_client(
        context, client_id=client["id"], package_id=package["id"], price=package_price
    )
    register_clients_to_event(context, event["uid"], [client["id"]])
    seeded = {
        "client": {
            "id": client["id"],
            "name": client["full_name"],
            "email": email,
            "portal_token": client["token"],
        },
        "service": service,
        "event": event,
        "package": package,
    }
    context.setdefault("event_payments", {}).update(seeded)
    return seeded


def seed_event_with_client(
    context: dict, *, service_name: str, price: str | int,
    first: str, last: str, email: str,
) -> dict:
    """Background helper: create client + event service + event + register the client.

    Stores the seeded entities in context under ``event_payments`` and returns them."""
    client = create_client(context, first, last, email)
    service = create_event_service(context, service_name, price)
    event = schedule_event(context, service)
    register_clients_to_event(context, event["uid"], [client["id"]])
    seeded = {
        "client": {
            "id": client["id"],
            "name": client["full_name"],
            "email": email,
            "portal_token": client["token"],
        },
        "service": service,
        "event": event,
    }
    context.setdefault("event_payments", {}).update(seeded)
    return seeded
