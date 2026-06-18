"""CP multi-booking — summary component displays correctly (VCITA2-14228).

Migrated from multi-booking.feature scenario "Summary component display correctly". As an
anonymous client: pick "Schedule Now" on the livesite, select service1 + service2, verify the
multi-booking summary (location At TLV, duration 1 hour, default staff), complete the booking
with client details, verify the confirmation, then verify the CP meeting page shows service1
"Pending approval" linked to service2.
"""

from playwright.sync_api import Page

from tests.tempo.scheduling.cp_multi_booking.cp_multi_booking_helpers import (
    assert_booking_confirmation,
    assert_meeting,
    assert_summary_component,
    fill_intake_and_confirm,
    open_meeting,
    pick_default_timeslot_and_continue,
    schedule_now,
    select_services,
)


def test_summary_component(page: Page, context: dict) -> None:
    seq = context["mb"]["seq"]
    owner_display_name = context["mb"]["owner_display_name"]

    schedule_now(page, context)
    print("  [OK] Opened the CP scheduler via the livesite 'Schedule Now' action")

    select_services(page, ["service1", "service2"])
    pick_default_timeslot_and_continue(page)
    print("  [OK] Selected service1 + service2 and continued from the calendar")

    assert_summary_component(
        page,
        location="At TLV",
        duration="Duration: 1 hour",
        providing_staff=f"With {owner_display_name}",
    )
    print("  [OK] Summary shows At TLV, Duration: 1 hour, default staff")

    fill_intake_and_confirm(
        page, first_name="jimmy", last_name="slipping", email=f"test8+{seq}@vmeetme.com"
    )
    assert_booking_confirmation(page, title="Booking request sent!")
    print("  [OK] Booking confirmation: 'Booking request sent!'")

    open_meeting(page, "service1")
    assert_meeting(
        page, meeting_name="service1", meeting_state="Pending approval", linked_bookings="service2"
    )
    print("  [OK] Meeting page shows service1 Pending approval, linked to service2")
