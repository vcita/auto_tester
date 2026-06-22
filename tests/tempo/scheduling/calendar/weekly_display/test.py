from playwright.sync_api import Page

from tests.tempo.scheduling.calendar.calendar_helpers import (
    assert_calendar_items,
    assert_current_display_state,
    schedule_appointment_from_calendar,
    schedule_event_from_calendar,
    set_content_display,
)


def test_weekly_display(page: Page, context: dict) -> None:
    client_name = context["created_client_name"]
    event_name = context["calendar_services"]["event1"]["name"]

    for appointment in [
        {"service_name": "service1", "client_name": client_name, "display": "Week", "navigate_to": "next", "timeslot": "wednesday,08:00 am", "meeting_identifier": "meeting1"},
        {"service_name": "service2", "client_name": client_name, "display": "Week", "navigate_to": "previous", "timeslot": "friday,03:00 am", "meeting_identifier": "meeting2"},
        {"service_name": "service2", "client_name": client_name, "display": "Week", "navigate_to": "next", "timeslot": "monday,03:00 pm", "start_time": "05:00 PM", "client_confirmation": "Checked", "meeting_identifier": "meeting3"},
    ]:
        schedule_appointment_from_calendar(page, context, appointment)

    schedule_event_from_calendar(
        page,
        context,
        {"service_name": "event1", "display": "Week", "navigate_to": "next", "timeslot": "wednesday,09:00 pm", "recurrence": "2 Day", "ends": "After:5"},
    )
    set_content_display(page, interval="30 minutes")

    assert_calendar_items(
        page,
        "next",
        "Week",
        [
            {"item_type": "appointment", "state": "invited", "item_title": client_name, "item_subtitle": context["calendar_services"]["service2"]["name"], "item_times": "5 - 6:30pm"},
            {"item_type": "appointment", "state": "scheduled", "item_title": client_name, "item_subtitle": context["calendar_services"]["service1"]["name"], "item_times": "8 - 9am"},
            {"item_type": "event", "state": "scheduled", "item_subtitle": event_name, "attendance": "0/2", "item_times": "9 - 10pm"},
            {"item_type": "event", "state": "scheduled", "item_subtitle": event_name, "attendance": "0/2", "item_times": "9 - 10pm"},
        ],
    )

    page.reload(wait_until="domcontentloaded")
    assert_current_display_state(page, "week", "1")
