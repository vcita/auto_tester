# Source: tests/scheduling/appointments/schedule_appointments/additional_recipients/script.md
# Migrated from automation-js/features/tempo/scheduling-appointments.feature (VCITA2-14025)

from playwright.sync_api import Page

from tests.tempo.scheduling.appointments.schedule_appointments.schedule_appointments_ui import (
    assert_meeting,
    schedule_appointment,
)


def test_additional_recipients(page: Page, context: dict) -> None:
    """Schedule two appointments with additional recipients - a typed email and one chosen
    "from list" - and verify the recipient appears on each appointment detail page."""
    data = context["schedule_appts"]
    service = data["service"]["name"]
    client = data["client"]["full_name"]
    recipient = f"test2+{data['seq']}@vmeetme.com"

    print(f"  Step 1: Schedule '{service}' for '{client}' with typed recipient {recipient}")
    meeting1 = schedule_appointment(
        page, context, service_name=service, client_name=client,
        additional_recipients=f"{recipient},",
    )
    assert_meeting(
        page, meeting1, service_name=service, client_name=client,
        additional_recipients=recipient,
    )

    print("  Step 2: Schedule another, choosing the recipient from the existing list")
    meeting2 = schedule_appointment(
        page, context, service_name=service, client_name=client,
        additional_recipients="from list",
    )
    assert_meeting(
        page, meeting2, service_name=service, client_name=client,
        additional_recipients=recipient,
    )

    print(f"  [OK] both appointments show additional recipient '{recipient}'")
