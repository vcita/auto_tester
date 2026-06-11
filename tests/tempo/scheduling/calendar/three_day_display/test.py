from playwright.sync_api import Page

from tests.tempo.scheduling.calendar.calendar_helpers import (
    assert_calendar_items,
    assert_current_display_state,
    assert_slot_color_mode,
    schedule_appointment_from_calendar,
    schedule_event_from_calendar,
    set_content_display,
)


def test_three_day_display(page: Page, context: dict) -> None:
    client_name = context["created_client_name"]
    event_name = context["calendar_services"]["event1"]["name"]
    set_content_display(page, interval="15 minutes", slot_colors="service")

    for appointment in [
        {"service_name": "service1", "client_name": client_name, "display": "3 Days", "navigate_to": "previous", "timeslot": "left,10:15 pm", "meeting_identifier": "meeting1"},
        {"service_name": "service1", "client_name": client_name, "display": "3 Days", "timeslot": "right,01:00 am", "client_confirmation": "Checked", "meeting_identifier": "meeting2"},
        {"service_name": "service2", "client_name": client_name, "display": "3 Days", "navigate_to": "next", "timeslot": "middle,03:00 pm", "meeting_identifier": "meeting3"},
        {"service_name": "service3", "client_name": client_name, "display": "3 Days", "navigate_to": "previous", "timeslot": "right,04:00 am", "meeting_identifier": "meeting4"},
    ]:
        schedule_appointment_from_calendar(page, context, appointment)

    schedule_event_from_calendar(
        page,
        context,
        {"service_name": "event1", "display": "3 Days", "navigate_to": "next", "timeslot": "right,01:00 pm", "end_time": "03:00 PM"},
    )

    expected_items = [
        {"item_type": "appointment", "state": "scheduled", "item_title": client_name, "item_subtitle": context["calendar_services"]["service2"]["name"], "item_times": "3 - 4:30pm"},
        {"item_type": "event", "state": "scheduled", "item_subtitle": event_name, "attendance": "0/2", "item_times": "1 - 3pm"},
    ]
    assert_calendar_items(page, "next", "3 Days", expected_items)
    assert_slot_color_mode(page, context, "next", "3 Days", expected_items, "service")

    page.reload(wait_until="domcontentloaded")
    assert_current_display_state(page, "threeDay", "1")
