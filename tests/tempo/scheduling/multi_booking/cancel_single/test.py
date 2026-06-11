"""Cancel a single linked appointment from a multi-service booking.

Migrated from automation-js multi-booking-appointments.feature scenario
"Cancel single multi-booking appointment".
"""

from playwright.sync_api import Page

from tests.tempo.scheduling.multi_booking.multi_booking_api import appointment_ids, wait_for_new_appointments
from tests.tempo.scheduling.multi_booking.multi_booking_ui import (
    appointment_is_free,
    cancel_appointment_bulk,
    linked_booking_count,
    open_appointment,
    read_appointment_state,
    read_linked_booking_description,
    read_linked_booking_services,
    schedule_multi_booking,
)

LINKED_DESCRIPTION = "Multi-service booking"


def test_cancel_single(page: Page, context: dict) -> None:
    service_names = context["mb_service_names"]
    client_name = context["mb_client_name"]

    print("  Phase A: Schedule a 3-service linked appointment")
    before = appointment_ids(context)
    schedule_multi_booking(page, context, service_names, client_name)

    new_by_id = wait_for_new_appointments(context, before, expected=3)
    service_to_id = {appt.get("title"): aid for aid, appt in new_by_id.items()}
    for name in service_names:
        if name not in service_to_id:
            raise AssertionError(
                f"Scheduled appointment for '{name}' not found. Titles seen: {list(service_to_id)}"
            )

    print("  Phase B: Cancel only the first linked appointment (service1)")
    open_appointment(page, service_to_id[service_names[0]])
    cancel_appointment_bulk(page, cancel_all=False)

    print("  Phase C: Verify the cancelled appointment is Cancelled, Free and unlinked")
    open_appointment(page, service_to_id[service_names[0]])
    state = read_appointment_state(page)
    assert state.upper() == "CANCELLED", f"service1 state expected CANCELLED, got '{state}'"
    assert appointment_is_free(page), "service1 expected to be Free"
    assert read_linked_booking_description(page) is None, (
        "service1 should no longer be linked after a single cancel"
    )

    print("  Phase D: Verify the other two stay Scheduled and linked (count 2)")
    remaining = service_names[1:]
    for name in remaining:
        open_appointment(page, service_to_id[name])
        state = read_appointment_state(page)
        assert state.upper() == "SCHEDULED", f"{name} state expected SCHEDULED, got '{state}'"
        assert appointment_is_free(page), f"{name} expected to be Free"
        description = read_linked_booking_description(page)
        assert description and LINKED_DESCRIPTION in description, (
            f"{name} expected a '{LINKED_DESCRIPTION}' linked description, got '{description}'"
        )
        count = linked_booking_count(description)
        assert count == str(len(remaining)), (
            f"{name} expected linked count {len(remaining)}, got '{count}'"
        )
        listed = read_linked_booking_services(page)
        for linked_name in remaining:
            assert linked_name in listed, (
                f"{name} linked-booking dialog missing '{linked_name}'. Listed: {listed}"
            )

    print("  [OK] Single linked appointment cancelled; remaining two stay scheduled and linked")
