"""Cancel all linked appointments from a multi-service booking.

Migrated from automation-js multi-booking-appointments.feature scenario
"Cancel all multi-booking appointment".
"""

from playwright.sync_api import Page

from tests.scheduling.multi_booking.multi_booking_api import appointment_ids, wait_for_new_appointments
from tests.scheduling.multi_booking.multi_booking_ui import (
    cancel_appointment_bulk,
    open_appointment,
    read_appointment_state,
    read_last_linked_booking_bubble,
    schedule_multi_booking,
)


def test_cancel_all(page: Page, context: dict) -> None:
    service_names = context["mb_service_names"]
    client_name = context["mb_client_name"]
    client_id = context["mb_client_id"]

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

    print("  Phase B: Cancel all linked appointments at once")
    open_appointment(page, service_to_id[service_names[0]])
    cancel_appointment_bulk(page, cancel_all=True)

    print("  Phase C: Verify all three appointments are Cancelled")
    for name in service_names:
        open_appointment(page, service_to_id[name])
        state = read_appointment_state(page)
        assert state.upper() == "CANCELLED", f"{name} state expected CANCELLED, got '{state}'"

    print("  Phase D: Verify the conversation cancelled linked-booking bubble")
    bubble = read_last_linked_booking_bubble(page, client_id)
    for name in service_names:
        assert any(name in service for service in bubble["services"]), (
            f"linked-booking bubble missing '{name}'. Bubble services: {bubble['services']}"
        )
    cancelled_shown = "CANCELLED" in bubble["labels"] or "CANCELLED" in bubble["text"].upper()
    assert cancelled_shown, (
        f"linked-booking bubble expected a CANCELLED state, got labels={bubble['labels']}"
    )

    print("  [OK] All linked appointments cancelled; conversation bubble shows the 3 cancelled services")
