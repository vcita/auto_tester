from playwright.sync_api import Page

from tests.scheduling.calendar.calendar_helpers import (
    assert_calendar_items,
    assert_current_display_state,
    schedule_appointment_from_calendar,
    schedule_event_from_calendar,
)


def test_monthly_display(page: Page, context: dict) -> None:
    client_name = context["created_client_name"]
    event_name = context["calendar_services"]["event1"]["name"]

    appointments = [
        {"service_name": "service1", "client_name": client_name, "display": "Month", "navigate_to": "previous", "timeslot": "20", "switch_all_day": "not_all_day", "meeting_identifier": "meeting1"},
        {"service_name": "service1", "client_name": client_name, "display": "Month", "navigate_to": "next", "timeslot": "1", "start_time": "01:00 AM", "end_time": "05:00 AM", "switch_all_day": "all_day", "meeting_identifier": "meeting2"},
        {"service_name": "service2", "client_name": client_name, "display": "Month", "navigate_to": "next", "timeslot": "3", "meeting_date": "next_week", "start_time": "03:00 AM", "end_time": "03:30 AM", "switch_all_day": "not_all_day", "meeting_identifier": "meeting3"},
    ]
    for appointment in appointments:
        schedule_appointment_from_calendar(page, context, appointment)

    schedule_event_from_calendar(
        page,
        context,
        {"service_name": "event1", "display": "Month", "navigate_to": "next", "timeslot": "5", "start_time": "10:00 AM", "recurrence": "3 Week", "ends": "After:10"},
    )

    assert_calendar_items(
        page,
        "next",
        "Month",
        [
            {"item_type": "appointment", "state": "scheduled", "item_title": client_name, "item_times": "1am"},
            {"item_type": "event", "state": "scheduled", "attendance": f"0/2 {event_name}", "item_times": "10am"},
            {"item_type": "appointment", "state": "scheduled", "item_title": client_name, "item_times": "3am"},
            {"item_type": "event", "state": "scheduled", "attendance": f"0/2 {event_name}", "item_times": "10am"},
        ],
    )

    page.reload(wait_until="domcontentloaded")
    assert_current_display_state(page, "month", "1")
