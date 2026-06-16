# Source: tests/scheduling/appointments/schedule_appointments/reschedule_cancel/script.md
# Migrated from automation-js/features/tempo/scheduling-appointments.feature (VCITA2-14025)

from playwright.sync_api import Page

from tests.tempo.scheduling.appointments.schedule_appointments.schedule_appointments_ui import (
    assert_meeting,
    cancel_appointment,
    reschedule_appointment,
    schedule_appointment,
)


def test_reschedule_cancel(page: Page, context: dict) -> None:
    """Schedule a past (COMPLETED) appointment, reschedule it to next week (SCHEDULED),
    then cancel it (CANCELLED), verifying state and times at each step."""
    data = context["schedule_appts"]
    service = data["service"]["name"]
    client = data["client"]["full_name"]

    print(f"  Step 1: Schedule past '{service}' for '{client}' (01:00 AM - 05:00 AM)")
    appt_id = schedule_appointment(
        page, context,
        service_name=service, client_name=client,
        meeting_date="previous_month", start_time="01:00 AM", end_time="05:00 AM",
    )
    assert_meeting(
        page, appt_id, service_name=service, client_name=client,
        state="COMPLETED", start_time="1:00 AM", end_time="5:00 AM",
    )

    print("  Step 2: Reschedule to next week (3:00am - 4:00am)")
    reschedule_appointment(
        page, appt_id, new_date="next_week", start_time="3:00am", end_time="4:00am"
    )
    assert_meeting(
        page, appt_id, service_name=service, client_name=client,
        state="SCHEDULED", start_time="3:00 AM", end_time="4:00 AM",
    )

    print("  Step 3: Cancel the appointment")
    cancel_appointment(page, appt_id)
    assert_meeting(
        page, appt_id, service_name=service, client_name=client,
        state="CANCELLED", start_time="3:00 AM", end_time="4:00 AM",
    )

    print("  [OK] scheduled COMPLETED -> rescheduled SCHEDULED -> CANCELLED")
