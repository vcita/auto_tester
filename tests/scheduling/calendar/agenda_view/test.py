from playwright.sync_api import Page

from tests.scheduling.calendar.calendar_api import (
    create_appointment_via_api,
    create_event_via_api,
    create_v2_staff,
    service_refs,
    unique_email,
)
from tests.scheduling.appointments.appointment_helpers import open_calendar_page
from tests.scheduling.calendar.calendar_helpers import assert_calendar_items, assert_current_display_state, select_staff_filter


def test_agenda_view(page: Page, context: dict) -> None:
    services = service_refs(context, ["service1", "service2", "event1"])
    staff1 = create_v2_staff(context, "Auto Staff1", unique_email("staff1"), "Manager", services)
    staff2 = create_v2_staff(context, "Auto Staff2", unique_email("staff2"), "User", services)
    context.setdefault("calendar_staff", []).extend([staff1, staff2])

    client = context["calendar_client"]
    create_appointment_via_api(context, "service1", client, "next_day_4", "15:30", "Auto Staff1")
    create_appointment_via_api(context, "service2", client, "next_day_8", "07:00", "Auto Staff2")
    create_event_via_api(context, "event1", "next_day_5", "07:00", "Auto Staff2")

    # Staff created via API after the page loaded are absent from the calendar staff
    # filter until it is refreshed, so reload before selecting all staff.
    page.reload(wait_until="domcontentloaded")
    open_calendar_page(page)
    select_staff_filter(page, "all")

    assert_calendar_items(
        page,
        "current",
        "Agenda",
        [
            {"item_type": "appointment", "state": "scheduled", "item_title": f"{context['created_client_name']}, {context['calendar_services']['service1']['name']}", "item_times": "3:30 - 4:30pm"},
            {"item_type": "event", "state": "scheduled", "attendance": f"0/2 {context['calendar_services']['event1']['name']}", "item_times": "7 - 8am"},
        ],
    )

    page.reload(wait_until="domcontentloaded")
    assert_current_display_state(page, "agenda", "0")
