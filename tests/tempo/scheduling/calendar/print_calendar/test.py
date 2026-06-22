from playwright.sync_api import Page

from tests.tempo.scheduling.calendar.calendar_helpers import schedule_appointment_from_calendar, trigger_calendar_print


def test_print_calendar(page: Page, context: dict) -> None:
    schedule_appointment_from_calendar(
        page,
        context,
        {
            "service_name": "service1",
            "client_name": context["created_client_name"],
            "display": "Month",
            "navigate_to": "next",
            "timeslot": "20",
            "meeting_identifier": "meeting1",
        },
    )
    trigger_calendar_print(page)
