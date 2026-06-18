"""CP multi-booking — invalid service combination (VCITA2-14228).

Migrated from multi-booking.feature scenario "Client tries to select a none valid combination
of services". Creates the extra services (service3 f2f-client, service4 Staff2-only, event1
event, service6) and an event1 instance via API (prerequisites), then as an anonymous client:
pick "Schedule Now", select service1 and assert service3/service4/event1 become disabled,
deselect service1 and assert every service is enabled, select event1 and assert the scheduler
advances to the future-event step.
"""

from playwright.sync_api import Page

from tests.account_api import create_service_via_api
from tests.tempo.scheduling.cp_multi_booking.cp_multi_booking_helpers import (
    assert_next_step_future_event,
    assert_services_disabled_state,
    schedule_now,
    schedule_event_via_api,
    toggle_service,
)


def _create_scenario_services(context: dict) -> dict:
    """Create the scenario-2 services via API (legacy 'user creates new service via API')."""
    staff2_uid = context["mb"]["staff2"]["uid"]
    # service3: f2f client location (legacy location_type=f2f_client -> client_location).
    service3 = create_service_via_api(
        context, "service3", duration=20, interaction_type="client_location"
    )
    # service4: assigned only to Staff2 (60m).
    service4 = create_service_via_api(
        context, "service4", staff_uids=[staff2_uid], duration=60
    )
    # event1: an event service (30m).
    event1 = create_service_via_api(
        context, "event1", duration=30, service_type="event"
    )
    # service6: plain appointment (30m).
    service6 = create_service_via_api(context, "service6", duration=30)
    return {"service3": service3, "service4": service4, "event1": event1, "service6": service6}


def test_invalid_combination(page: Page, context: dict) -> None:
    print("  Step 1: Create service3/service4/event1/service6 via API")
    services = _create_scenario_services(context)

    print("  Step 2: Schedule an event1 instance via API")
    schedule_event_via_api(context, services["event1"])

    schedule_now(page, context)
    print("  [OK] Opened the CP scheduler via the livesite 'Schedule Now' action")

    toggle_service(page, "service1")
    print("  [OK] Selected service1")

    assert_services_disabled_state(
        page, {"service3": True, "service4": True, "event1": True}
    )
    print("  [OK] service3/service4/event1 are disabled while service1 is selected")

    toggle_service(page, "service1")
    print("  [OK] Deselected service1")

    assert_services_disabled_state(
        page,
        {
            "service1": False,
            "service2": False,
            "service3": False,
            "service4": False,
            "service6": False,
            "event1": False,
            "In-office appointment": False,
            "Introductory phone call": False,
        },
    )
    print("  [OK] All services enabled after deselecting service1")

    toggle_service(page, "event1")
    assert_next_step_future_event(page)
    print("  [OK] Selecting event1 advanced the scheduler to the future-event step")
