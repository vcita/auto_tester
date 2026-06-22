"""API seeds for the payments_emails migration (VCITA2-14027).

Mirrors the per-scenario API prerequisites of
``automation-js/features/salsa/payments-emails.feature``: a client, appointment
services (legacy ``payment_setting`` -> ``charge_type``), API-scheduled
appointments, payable products + product assignments, packages, and estimates.

Appointment data is stored in the shared ``appointment_payments`` context store so
the reused appointment_payments_helpers (open_appointment, invoice_appointment,
pay_for_appointment, record_appt_payment_via_pos) work unchanged. The UI actions
that actually send the client emails (send-link, invoice, pay, record, POS) live in
the test bodies, not here.
"""

from __future__ import annotations

import time

from tests.account_api import (
    account_request,
    assign_package_to_client,
    create_package_via_api,
)
from tests.salsa.payments.appointment_payments.appointment_payments_api import (
    seed_client,
    seed_service,
    schedule_appointment,
)
from tests.salsa.payments.deposits.deposits_api import create_estimate_via_api, create_product

PRODUCT_ORDERS_PATH = "/business/payments/v1/product_orders"


def _store(context: dict) -> dict:
    return context.setdefault("payments_emails", {})


def _client(context: dict) -> dict:
    return context["appointment_payments"]["client"]


def new_client_email() -> str:
    return f"test+{int(time.time() * 1000)}@vmeetme.com"


def seed_client_service_appointment(context: dict, *, payment_setting: str,
                                    price: str | int = 100, service_name: str = "service",
                                    identifier: str = "api1", first: str = "first",
                                    last: str = "last", email: str | None = None) -> dict:
    """Background + a service (suggest/require to pay) + one API appointment."""
    email = email or new_client_email()
    seed_client(context, first=first, last=last, email=email)
    service = seed_service(context, name=service_name, payment_setting=payment_setting, price=price)
    schedule_appointment(context, service=service, identifier=identifier)
    _store(context)["client_email"] = email
    _store(context)["client_name"] = f"{first} {last}"
    return _store(context)


def seed_client_and_service(context: dict, *, payment_setting: str, price: str | int = 100,
                            service_name: str = "service", first: str = "first",
                            last: str = "last", email: str | None = None) -> dict:
    """Background + a service only (no appointment), for the package scenario."""
    email = email or new_client_email()
    seed_client(context, first=first, last=last, email=email)
    service = seed_service(context, name=service_name, payment_setting=payment_setting, price=price)
    _store(context)["client_email"] = email
    _store(context)["client_name"] = f"{first} {last}"
    return service


def seed_extra_appointment(context: dict, *, payment_setting: str, price: str | int = 100,
                           service_name: str = "service2", identifier: str = "api2") -> dict:
    """Schedule a second API appointment on its own service (so the Orders-routed
    invoice can target it unambiguously)."""
    service = seed_service(context, name=service_name, payment_setting=payment_setting, price=price)
    return schedule_appointment(context, service=service, identifier=identifier)


def seed_product_and_assign(context: dict, *, name: str = "product21", price: str | int = 10,
                            description: str = "description for payable item1") -> dict:
    """Create a payable product and assign it to the seeded client (product order).

    The assignment gives the client an open payment request to close/record so the
    confirmation-email scenarios have a balance to settle."""
    product = create_product(context, name, str(price), description=description)
    account_request(context, "POST", PRODUCT_ORDERS_PATH, json={
        "new_api": True,
        "product_order": {
            "client_id": _client(context)["id"],
            "product_id": product["id"],
            "price": product["price"],
            "tax_ids": [],
        },
    })
    _store(context)["product"] = product
    return product


def seed_package(context: dict, *, name: str = "package", credits: int = 2,
                 price: str | int = 150) -> dict:
    """Create a specific-service package (NOT assigned).

    Assigning it to the client is the in-scope action under test, so it is done in
    the test body (assign_package_to_client) where the resulting client-facing
    'Your new "<name>" package information and details' email is verified."""
    service = context["appointment_payments"]["service"]
    package = create_package_via_api(
        context, name,
        services=[{
            "id": service["id"], "name": service["name"],
            "price": str(service.get("price", "")), "currency": "USD",
        }],
        total_bookings=credits, price=str(price),
    )
    _store(context)["package"] = package
    _store(context)["package_price"] = str(price)
    return package


def assign_seeded_package(context: dict) -> dict:
    """Assign the seeded package to the seeded client via API (the action under test)."""
    package = _store(context)["package"]
    return assign_package_to_client(
        context, _client(context)["id"], package["id"], _store(context)["package_price"]
    )


def seed_client_and_product(context: dict, *, product_name: str = "product21",
                            price: str | int = 10,
                            description: str = "description for payable item21",
                            first: str = "first", last: str = "last") -> dict:
    """Background client + a payable product, for the estimate-mail CP scenario.

    The estimate itself is created in the test body (it is the action that sends the
    "New estimate from ..." email being verified)."""
    from tests.account_api import create_client
    email = new_client_email()
    client = create_client(context, first, last, email)
    product = create_product(context, product_name, str(price), description=description)
    store = _store(context)
    store["client"] = {"id": client["id"], "name": f"{first} {last}",
                       "portal_token": client.get("token"), "email": email}
    store["product"] = product
    return product


def create_estimate_email_action(context: dict, *, title: str = "bestimate",
                                 address: str = "Babylon, persia") -> dict:
    """Create the estimate (send_email=True) against the seeded client + product.

    Returns the created estimate; the platform sends the client the
    "New estimate from <business>" email on creation (the action under test)."""
    store = _store(context)
    estimate = create_estimate_via_api(
        context, title, {"id": store["client"]["id"]}, [store["product"]],
        address=address, send_email=True, is_signature_required=False,
    )
    store["estimate"] = estimate
    return estimate
