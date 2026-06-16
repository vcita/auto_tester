"""API seeds for the appointment_payments migration (VCITA2-13857).

Mirrors automation-js/features/salsa/appointment-payments.feature Background plus
per-scenario prerequisites: a client, one or more appointment services (legacy
``payment_setting`` -> ``charge_type``), API-scheduled appointments, taxes, and
packages. UI-only prerequisites (the redeem-with-package checkbox, completing an
appointment) are performed in the test bodies, not here.
"""

from __future__ import annotations

from tests.account_api import (
    assign_package_to_client,
    create_appointment_via_api,
    create_client,
    create_package_via_api,
    create_service_via_api,
    future_appointment_start_time,
)
from tests.salsa.products.products_account import create_tax_via_api

# Legacy payment_setting -> charge_type (automation-js api/service.js _setPaymentType)
CHARGE_TYPE = {
    "require to pay": "paid_force",
    "suggest to pay": "paid",
    "display a fee": "paid_non_secured",
    "display for a fee": "discuss",
}


def _store(context: dict) -> dict:
    return context.setdefault("appointment_payments", {})


def seed_client(context: dict, *, first: str, last: str, email: str) -> dict:
    """Create the scenario client and cache it under appointment_payments."""
    client = create_client(context, first, last, email)
    client_name = client.get("full_name") or f"{first} {last}"
    record = {
        "id": client["id"],
        "name": client_name,
        "first": first,
        "portal_token": client.get("token"),
    }
    _store(context)["client"] = record
    return record


def seed_service(context: dict, *, name: str, payment_setting: str,
                 price: str | int | None) -> dict:
    """Create an appointment service for the given legacy payment_setting."""
    service = create_service_via_api(
        context, name, charge_type=CHARGE_TYPE[payment_setting],
        price=None if price is None else str(price),
    )
    if price is not None:
        service["price"] = str(price)
    _store(context).setdefault("services", {})[name] = service
    _store(context)["service"] = service
    return service


def schedule_appointment(context: dict, *, service: dict, identifier: str | None = None,
                         lead_days: int | None = None) -> dict:
    """Schedule an appointment via API and cache it under bookings by identifier.

    `identifier` mirrors the legacy meeting_identifier alias (defaults to the
    service name, matching the feature's default). `lead_days` overrides the
    start time (negative => past) so "display a fee" appointments can be marked
    completed and become DUE, mirroring the legacy near-now UI scheduling."""
    client = _store(context)["client"]
    start_time = None if lead_days is None else future_appointment_start_time(lead_days)
    booking = create_appointment_via_api(context, service, {"id": client["id"]}, start_time=start_time)
    booking_id = booking.get("id") or booking.get("uid")
    if not booking_id:
        raise ValueError(f"Appointment API response missing id: {booking}")
    alias = identifier or service["name"]
    record = {"id": booking_id, "identifier": alias, "service_name": service["name"]}
    _store(context).setdefault("bookings", {})[alias] = record
    _store(context)["last_booking"] = record
    return record


def seed_appointment(context: dict, *, service_name: str, payment_setting: str,
                     price: str | int | None, first: str, last: str, email: str,
                     identifier: str | None = None) -> dict:
    """Background + one API appointment: client, service, scheduled appointment."""
    seed_client(context, first=first, last=last, email=email)
    service = seed_service(context, name=service_name,
                           payment_setting=payment_setting, price=price)
    schedule_appointment(context, service=service, identifier=identifier)
    return _store(context)


def seed_tax(context: dict, *, name: str, rate: int) -> dict:
    tax = create_tax_via_api(context, name, rate)
    _store(context)["tax"] = tax
    return tax


def seed_package(context: dict, *, name: str, service: dict, credits: int,
                 price: str | int) -> dict:
    """Create a specific-service package and assign it to the seeded client."""
    package = create_package_via_api(
        context, name,
        services=[{
            "id": service["id"], "name": service["name"],
            "price": str(service.get("price", "")), "currency": "USD",
        }],
        total_bookings=credits, price=str(price),
    )
    client = _store(context)["client"]
    assign_package_to_client(context, client["id"], package["id"], str(price))
    _store(context)["package"] = package
    return package
