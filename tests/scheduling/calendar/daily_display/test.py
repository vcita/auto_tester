from playwright.sync_api import Page

from tests.scheduling.calendar.calendar_helpers import (
    assert_calendar_items,
    assert_current_display_state,
    assert_slot_color_mode,
    schedule_appointment_from_calendar,
    schedule_event_from_calendar,
    set_content_display,
)


def test_daily_display(page: Page, context: dict) -> None:
    client_name = context["created_client_name"]
    event_name = context["calendar_services"]["event1"]["name"]
    set_content_display(page, interval="30 minutes", slot_colors="staff")

    for appointment in [
        {"service_name": "service1", "client_name": client_name, "display": "Day", "navigate_to": "next", "timeslot": "10:30 pm", "meeting_identifier": "meeting1"},
        {"service_name": "service2", "client_name": client_name, "display": "Day", "navigate_to": "previous", "timeslot": "03:00 am", "meeting_identifier": "meeting2"},
        {"service_name": "service3", "client_name": client_name, "display": "Day", "timeslot": "04:00 am", "meeting_date": "last_week", "meeting_identifier": "meeting3"},
    ]:
        schedule_appointment_from_calendar(page, context, appointment)

    schedule_event_from_calendar(
        page,
        context,
        {"service_name": "event1", "display": "Day", "navigate_to": "previous", "timeslot": "all_day", "recurrence": "3 Month", "ends": "After:4"},
    )

    expected_items = [
        {"item_type": "event", "state": "completed", "item_subtitle": event_name, "attendance": "0/2", "item_times": "12 - 1am"},
        {"item_type": "appointment", "state": "completed", "item_title": client_name, "item_subtitle": context["calendar_services"]["service2"]["name"], "item_times": "3 - 4:30am"},
    ]
    assert_calendar_items(page, "previous", "Day", expected_items)
    assert_slot_color_mode(page, context, "previous", "Day", expected_items, "staff")

    page.reload(wait_until="domcontentloaded")
    assert_current_display_state(page, "singleDay", "-1")
