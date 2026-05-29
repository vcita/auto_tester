from playwright.sync_api import Page

from tests.scheduling.calendar.calendar_api import create_v2_staff, service_refs, unique_email
from tests.scheduling.calendar.calendar_helpers import (
    assert_calendar_items,
    assert_calendar_items_absent,
    schedule_appointment_from_calendar,
    select_staff_filter,
    switch_logged_in_staff,
)


def test_display_multiple_staff(page: Page, context: dict) -> None:
    services = service_refs(context, ["service1", "service2"])
    staff1 = _get_or_create_staff(context, "Auto Staff1", "Manager", services)
    staff2 = _get_or_create_staff(context, "Auto Staff2", "User", services)
    calendar_staff = context.setdefault("calendar_staff", [])
    for staff in (staff1, staff2):
        if staff not in calendar_staff:
            calendar_staff.append(staff)
    client_name = context["created_client_name"]

    schedule_appointment_from_calendar(
        page,
        context,
        {"service_name": "service1", "client_name": client_name, "display": "Month", "navigate_to": "next", "timeslot": "10", "start_time": "03:30 AM", "end_time": "04:30 AM", "assigned_staff": "Auto Staff1", "meeting_identifier": "meeting1"},
    )
    schedule_appointment_from_calendar(
        page,
        context,
        {"service_name": "service2", "client_name": client_name, "display": "Month", "navigate_to": "next", "timeslot": "10", "start_time": "07:00 AM", "end_time": "08:30 AM", "assigned_staff": "Auto Staff2", "meeting_identifier": "meeting2"},
    )

    select_staff_filter(page, "Auto Staff1")
    assert_calendar_items(page, "next", "Month", [{"item_type": "appointment", "state": "scheduled", "item_title": client_name, "item_times": "3:30am"}])
    assert_calendar_items_absent(page, "next", "Month", [{"item_type": "appointment", "state": "scheduled", "item_title": client_name, "item_times": "7am"}])

    select_staff_filter(page, "Auto Staff2")
    assert_calendar_items(page, "next", "Month", [{"item_type": "appointment", "state": "scheduled", "item_title": client_name, "item_times": "7am"}])
    assert_calendar_items_absent(page, "next", "Month", [{"item_type": "appointment", "state": "scheduled", "item_title": client_name, "item_times": "3:30am"}])

    select_staff_filter(page, "all")
    assert_calendar_items(
        page,
        "next",
        "Month",
        [
            {"item_type": "appointment", "state": "scheduled", "item_title": client_name, "item_times": "3:30am"},
            {"item_type": "appointment", "state": "scheduled", "item_title": client_name, "item_times": "7am"},
        ],
    )
    switch_logged_in_staff(page, context, staff2)
    assert_calendar_items(page, "next", "Month", [{"item_type": "appointment", "state": "scheduled", "item_title": client_name, "item_times": "7am"}])

def _get_or_create_staff(context: dict, name: str, role: str, services: list[dict]) -> dict:
    for staff in context.get("calendar_staff", []):
        if staff.get("display_name") == name or staff.get("name") == name:
            return staff
    return create_v2_staff(context, name, unique_email(name.lower().replace(" ", "")), role, services)
