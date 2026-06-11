# Source: tests/scheduling/appointments/multistaff/schedule_as_user_staff/script.md
# Migrated from automation-js/features/tempo/multistaff.feature (VCITA2-13950)

from playwright.sync_api import Page

from tests.tempo.scheduling.appointments.multistaff.multistaff_helpers import (
    meeting_name,
    meeting_text,
    open_meeting_page,
    schedule_appointment,
)
from tests.tempo.scheduling.calendar.calendar_helpers import switch_logged_in_staff


def test_schedule_as_user_staff(page: Page, context: dict) -> None:
    """Switch to a user-role staff (SSO), schedule an appointment, and the created meeting
    is assigned to that staff with the right client and price."""
    data = context["multistaff"]
    service = data["service"]["name"]
    client = data["client"]["full_name"]
    user_staff = data["user_staff"]

    print(f"  Step 1: Switch logged-in staff to '{user_staff['name']}' (SSO)")
    switch_logged_in_staff(page, context, user_staff)

    print(f"  Step 2: Schedule '{service}' for '{client}' as the switched-in staff")
    appointment_id = schedule_appointment(page, context, client, service)

    print("  Step 3: Verify meeting details")
    outer = open_meeting_page(page, appointment_id)
    name = meeting_name(outer)
    client_text = meeting_text(outer, "display-name")
    assigned = meeting_text(outer, "assigned-staff")
    price = meeting_text(outer, "balance-due-amount")

    assert service in name, f"expected service '{service}' in meeting header, got {name!r}"
    assert client in client_text, f"expected client '{client}', got {client_text!r}"
    assert user_staff["name"] in assigned, f"expected assigned '{user_staff['name']}', got {assigned!r}"
    assert "$1.00" in price, f"expected price '$1.00', got {price!r}"

    print(f"  [OK] meeting assigned to '{user_staff['name']}' with price $1.00")
