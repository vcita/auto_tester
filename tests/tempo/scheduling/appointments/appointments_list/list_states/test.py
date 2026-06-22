# Source: tests/scheduling/appointments/appointments_list/list_states/script.md
# Migrated from automation-js/features/tempo/appointments-list.feature (VCITA2-13953, scenario 1)

from playwright.sync_api import Page

from tests.account_api import create_appointment_via_api, future_appointment_start_time
from tests.tempo.scheduling.appointments.appointments_list.appointments_list_helpers import (
    assert_cp_conversation_includes,
    open_appointment_list,
    previous_month_appointment_start_time,
    search_appointments,
)


def test_list_states(page: Page, context: dict) -> None:
    """Appointments list page: empty state, one SCHEDULED appointment, two appointments
    (SCHEDULED + COMPLETED) with the CP "Appointment confirmed" conversation, then the
    COMPLETED state filter."""
    seeded = context["appointments_list"]
    client = seeded["client"]
    service = seeded["service"]
    service_name = service["name"]

    print("  Step 1: Empty state - search with no results")
    open_appointment_list(page, context)
    rows = search_appointments(page, context, [])
    assert rows == [], f"expected empty appointments list, got {rows}"

    print(f"  Step 2: Schedule '{service_name}' (future) via API -> SCHEDULED")
    create_appointment_via_api(
        context, service, client, start_time=future_appointment_start_time()
    )
    expected_one = [f"{service_name} SCHEDULED"]
    rows = search_appointments(page, context, expected_one)
    assert rows == expected_one, f"expected {expected_one}, got {rows}"

    print(f"  Step 3: Schedule '{service_name}' in the previous month via API -> COMPLETED")
    create_appointment_via_api(
        context, service, client, start_time=previous_month_appointment_start_time()
    )

    confirmed_title = f"Appointment confirmed: {service_name}"
    print(f"  Step 3a: Verify CP conversation includes '{confirmed_title}'")
    assert_cp_conversation_includes(page, context, client, confirmed_title)

    print("  Step 3b: Both appointments shown (SCHEDULED + COMPLETED)")
    expected_two = [f"{service_name} SCHEDULED", f"{service_name} COMPLETED"]
    rows = search_appointments(page, context, expected_two)
    assert rows == expected_two, f"expected {expected_two}, got {rows}"

    print("  Step 4: Filter by COMPLETED -> only the past appointment")
    expected_filtered = [f"{service_name} COMPLETED"]
    rows = search_appointments(page, context, expected_filtered, completed_filter=True)
    assert rows == expected_filtered, f"expected {expected_filtered}, got {rows}"

    print("  [OK] appointments list empty / one / two (+CP) / filtered verified")
