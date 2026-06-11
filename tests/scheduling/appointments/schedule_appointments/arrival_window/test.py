# Source: tests/scheduling/appointments/schedule_appointments/arrival_window/script.md
# Migrated from automation-js/features/tempo/scheduling-appointments.feature (VCITA2-14025)

from playwright.sync_api import Page

from tests.scheduling.appointments.schedule_appointments.schedule_appointments_api import (
    create_appointment_service,
    set_service_arrival_window,
    wait_for_client_email_texts,
)
from tests.scheduling.appointments.schedule_appointments.schedule_appointments_ui import (
    assert_meeting,
    reschedule_appointment,
    schedule_appointment,
)


def test_arrival_window(page: Page, context: dict) -> None:
    """Verify arrival-window resolution (account default, service override, in-dialog preset/custom,
    and reschedule override) on the appointment detail page and the client notification email."""
    data = context["schedule_appts"]
    service1 = data["service"]["name"]
    client = data["client"]["full_name"]
    owner_uid = data["owner"]["uid"]

    print("  Prereq: create 'service2' with a 15-minute arrival-window override (API)")
    service2 = create_appointment_service(context, "service2", staff_uids=[owner_uid])
    set_service_arrival_window(context, service2["id"], 15)
    service2_name = service2["name"]

    print("  Step 1: account default (service1=45m) vs service override (service2=15m) at 03:00 PM")
    meeting01 = schedule_appointment(
        page, context, service_name=service1, client_name=client,
        meeting_date="next_month", start_time="03:00 PM",
    )
    assert_meeting(
        page, meeting01, service_name=service1, client_name=client,
        arrival_window="3:00 pm - 3:45 pm",
    )
    meeting02 = schedule_appointment(
        page, context, service_name=service2_name, client_name=client,
        meeting_date="next_month", start_time="03:00 PM",
    )
    assert_meeting(
        page, meeting02, service_name=service2_name, client_name=client,
        arrival_window="3:00 pm - 3:15 pm",
    )
    wait_for_client_email_texts(context, ["Estimated arrival time:", "3:00 pm - 3:45 pm"])
    wait_for_client_email_texts(context, ["Estimated arrival time:", "3:00 pm - 3:15 pm"])

    print("  Step 2: in-dialog overrides preset '2 hours' and 'Custom 75' at 04:00 PM")
    meeting11 = schedule_appointment(
        page, context, service_name=service1, client_name=client,
        arrival_window="2 hours", meeting_date="next_month", start_time="04:00 PM",
    )
    assert_meeting(
        page, meeting11, service_name=service1, client_name=client,
        arrival_window="4:00 pm - 6:00 pm",
    )
    meeting12 = schedule_appointment(
        page, context, service_name=service2_name, client_name=client,
        arrival_window="Custom 75", meeting_date="next_month", start_time="04:00 PM",
    )
    assert_meeting(
        page, meeting12, service_name=service2_name, client_name=client,
        arrival_window="4:00 pm - 5:15 pm",
    )
    wait_for_client_email_texts(context, ["Estimated arrival time:", "4:00 pm - 6:00 pm"])
    wait_for_client_email_texts(context, ["Estimated arrival time:", "4:00 pm - 5:15 pm"])

    print("  Step 3: reschedule the '2 hours' appointment arrival window to '30 minutes'")
    reschedule_appointment(page, meeting11, arrival_window="30 minutes")
    assert_meeting(
        page, meeting11, service_name=service1, client_name=client,
        arrival_window="4:00 pm - 4:30 pm",
    )
    wait_for_client_email_texts(context, ["Estimated arrival time:", "4:00 pm - 4:30 pm"])

    print("  [OK] arrival window: default/override/preset/custom + reschedule verified (detail + email)")
