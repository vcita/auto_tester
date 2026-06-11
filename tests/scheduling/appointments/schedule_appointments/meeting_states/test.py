# Source: tests/scheduling/appointments/schedule_appointments/meeting_states/script.md
# Migrated from automation-js/features/tempo/scheduling-appointments.feature (VCITA2-14025)

from playwright.sync_api import Page

from tests.scheduling.appointments.schedule_appointments.schedule_appointments_ui import (
    assert_meeting,
    schedule_appointment,
)


def test_meeting_states(page: Page, context: dict) -> None:
    """Schedule from the BO creating a new client inline and assigning staff, exercising the three
    meeting states: INVITED (client confirmation), SCHEDULED (future all-day), COMPLETED (past)."""
    data = context["schedule_appts"]
    service = data["service"]["name"]
    user_staff = data["user_staff"]["name"]
    manager_staff = data["manager_staff"]["name"]

    print("  Step 1: New client + assigned existing staff + client confirmation -> INVITED")
    meeting1 = schedule_appointment(
        page, context, service_name=service,
        new_client={"first_name": "rick", "last_name": "morty", "email": f"client{data['seq']}@vmeetme.com"},
        assigned_staff=user_staff, client_confirmation=True,
    )
    assert_meeting(
        page, meeting1, service_name=service, client_name="rick morty",
        assigned_staff=user_staff, state="INVITED",
    )

    print("  Step 2: Manager staff + next-month all-day -> SCHEDULED")
    meeting2 = schedule_appointment(
        page, context, service_name=service, client_name="rick morty",
        assigned_staff=manager_staff,
        meeting_date="next_month", start_time="01:00 AM", end_time="05:00 AM", all_day=True,
    )
    assert_meeting(
        page, meeting2, service_name=service, client_name="rick morty",
        assigned_staff=manager_staff, state="SCHEDULED", meeting_date="next_month",
    )

    print("  Step 3: Existing client + manager staff + previous-month -> COMPLETED")
    meeting3 = schedule_appointment(
        page, context, service_name=service, client_name="rick morty",
        assigned_staff=manager_staff, meeting_date="previous_month",
    )
    assert_meeting(
        page, meeting3, service_name=service, client_name="rick morty",
        assigned_staff=manager_staff, state="COMPLETED", meeting_date="previous_month",
    )

    print("  [OK] INVITED -> SCHEDULED -> COMPLETED with inline new client + assigned staff")
