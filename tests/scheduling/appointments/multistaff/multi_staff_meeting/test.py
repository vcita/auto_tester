# Source: tests/scheduling/appointments/multistaff/multi_staff_meeting/script.md
# Migrated from automation-js/features/tempo/multistaff.feature (VCITA2-13950)

from playwright.sync_api import Page

from tests.scheduling.appointments.multistaff.multistaff_helpers import (
    meeting_name,
    meeting_text,
    open_meeting_page,
    remove_additional_staff,
    schedule_appointment,
)


def test_multi_staff_meeting(page: Page, context: dict) -> None:
    """Owner schedules a multi-staff appointment, removes one additional staff, and the
    meeting shows assigned staff = owner and additional staff = the remaining staff."""
    data = context["multistaff"]
    service = data["service"]["name"]
    client = data["client"]["full_name"]
    owner = data["owner"]["display_name"]
    user_staff = data["user_staff"]["name"]
    manager_staff = data["manager_staff"]["name"]

    print(f"  Step 1: Schedule '{service}' for '{client}' with {user_staff} + {manager_staff}")
    appointment_id = schedule_appointment(
        page, context, client, service, additional_staff=[user_staff, manager_staff]
    )

    print(f"  Step 2: Remove additional staff '{user_staff}' from the meeting")
    open_meeting_page(page, appointment_id)
    remove_additional_staff(page, user_staff)

    print("  Step 3: Verify meeting details")
    outer = open_meeting_page(page, appointment_id)
    name = meeting_name(outer)
    client_text = meeting_text(outer, "display-name")
    assigned = meeting_text(outer, "assigned-staff")
    additional = meeting_text(outer, "assigned-additional-staff")

    assert service in name, f"expected service '{service}' in meeting header, got {name!r}"
    assert client in client_text, f"expected client '{client}', got {client_text!r}"
    assert owner in assigned, f"expected assigned staff '{owner}', got {assigned!r}"
    assert manager_staff in additional, f"expected additional '{manager_staff}', got {additional!r}"
    assert user_staff not in additional, f"'{user_staff}' should have been removed, got {additional!r}"

    print(f"  [OK] meeting assigned to owner '{owner}', additional staff = '{manager_staff}' only")
