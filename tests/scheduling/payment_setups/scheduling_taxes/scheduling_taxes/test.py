"""Services and Scheduling with taxes (VCITA2-14008).

Migrated from payment-setups.feature scenario "Services and Scheduling with taxes": taxes
and the API ``suggest2pay`` service come from ``_setup``; this test creates the taxed UI
services, verifies the services-list tax text, schedules four appointments (one with a tax
override), verifies meeting prices and payment-request tax math, then flips ``tax_mode`` to
include and verifies the tax-inclusive amount.
"""

from playwright.sync_api import Page

from tests.payments.appointment_payments.appointment_payments_helpers import (
    assert_appt_payment_request,
)
from tests.payments.invoices.invoice_billing_api import set_tax_mode
from tests.scheduling.appointments.multistaff.multistaff_helpers import schedule_appointment
from tests.scheduling.payment_setups.payment_setups_ui import (
    create_service_ui,
    read_meeting_price,
)
from tests.scheduling.services_categories.services_categories_helpers import (
    assert_service_details,
)


def _register_booking(context: dict, identifier: str, appt_id: str) -> None:
    """Register a scheduled appointment in the appointment_payments store so the reused
    payment-request reader can navigate to it by identifier."""
    store = context.setdefault("appointment_payments", {}).setdefault("bookings", {})
    booking = {"id": appt_id}
    store[identifier] = booking
    context["appointment_payments"]["last_booking"] = booking


def test_scheduling_taxes(page: Page, context: dict) -> None:
    client_name = context["ps"]["client"]["name"]
    non_default = context["ps"]["taxes"]["non_default"]
    another = context["ps"]["taxes"]["another"]

    # 1) Create the three UI services (default 10% tax auto-applies to UI services).
    create_service_ui(page, "require2pay", "require to pay", "100")
    create_service_ui(page, "displayFree", "display free", None)
    create_service_ui(
        page, "another require", "require to pay", "100",
        taxes=[(non_default["name"], non_default["rate"])],
    )
    print("  [OK] Created the three taxed UI services")

    # 2) Services list: payment type + price + tax text.
    assert_service_details(page, "suggest2pay", contains=["$50"], excludes=["Tax"])
    assert_service_details(page, "require2pay", contains=["$100", "(+10% Tax)"])
    assert_service_details(page, "displayFree", contains=["Free"], excludes=["Tax"])
    assert_service_details(page, "another require", contains=["$100", "(+15% Tax)"])
    print("  [OK] Services list shows the expected tax text")

    # 3) Schedule four appointments (suggest2pay overrides the tax to another_tax 15%).
    _register_booking(context, "meeting1", schedule_appointment(page, context, client_name, "require2pay"))
    _register_booking(context, "meeting2", schedule_appointment(
        page, context, client_name, "suggest2pay",
        price_override={"taxes": [(another["name"], another["rate"])]},
    ))
    _register_booking(context, "meeting3", schedule_appointment(page, context, client_name, "displayFree"))
    _register_booking(context, "meeting4", schedule_appointment(page, context, client_name, "another require"))
    print("  [OK] Scheduled four appointments")

    # 4) Meeting details: free + taxed price.
    free_price = read_meeting_price(page, context["appointment_payments"]["bookings"]["meeting3"]["id"])
    assert free_price == "Free", f"displayFree meeting expected Free, got {free_price!r}"
    taxed_price = read_meeting_price(page, context["appointment_payments"]["bookings"]["meeting1"]["id"])
    assert "110.00" in taxed_price and "($100.00 + Tax)" in taxed_price, (
        f"require2pay meeting expected '110.00 ($100.00 + Tax)', got {taxed_price!r}"
    )
    print("  [OK] Meeting prices show the expected tax math")

    # 5) Payment requests (tax-exclusive mode).
    assert_appt_payment_request(page, context, {
        "state": "DUE", "amount": "$110.00 ($100.00 + Tax)",
        "service_name": "require2pay", "client_full_name": client_name,
    }, identifier="meeting1")
    assert_appt_payment_request(page, context, {
        "state": "NOT YET DUE", "amount": "$57.50 ($50.00 + Tax)",
        "service_name": "suggest2pay", "client_full_name": client_name,
    }, identifier="meeting2")
    assert_appt_payment_request(page, context, {
        "state": "DUE", "amount": "$115.00 ($100.00 + Tax)",
        "service_name": "another require", "client_full_name": client_name,
    }, identifier="meeting4")
    print("  [OK] Payment requests show the expected tax-exclusive amounts")

    # 6) tax_mode include: new appointment is tax-inclusive; the old one keeps its amount.
    set_tax_mode(context, "include")
    _register_booking(context, "meeting6", schedule_appointment(page, context, client_name, "require2pay"))
    assert_appt_payment_request(page, context, {
        "state": "DUE", "amount": "$100.00",
        "service_name": "require2pay", "client_full_name": client_name,
    }, identifier="meeting6")
    assert_appt_payment_request(page, context, {
        "state": "DUE", "amount": "$110.00 ($100.00 + Tax)",
        "service_name": "require2pay", "client_full_name": client_name,
    }, identifier="meeting1")
    print("  [OK] tax_mode include produces the tax-inclusive amount; prior request unchanged")
