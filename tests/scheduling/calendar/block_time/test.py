from playwright.sync_api import Page

from tests.scheduling.calendar.calendar_helpers import (
    add_blocked_time,
    assert_calendar_items,
    drag_calendar_item,
    edit_blocked_time,
    set_content_display,
)


def test_block_time(page: Page, context: dict) -> None:
    set_content_display(page, interval="30 minutes")
    add_blocked_time(
        page,
        {
            "display": "Week",
            "navigate_to": "next",
            "timeslot": "monday,10:00 am",
            "timeslot_end": "monday,12:00 pm",
            "title": "lunchtime",
        },
    )
    assert_calendar_items(page, "next", "Week", [{"item_type": "blocked_time", "item_title": "lunchtime"}])

    drag_calendar_item(page, "lunchtime", "Week", "next", "tuesday,12:00 pm")
    assert_calendar_items(page, "next", "Week", [{"item_type": "blocked_time", "item_title": "lunchtime"}])

    edit_blocked_time(page, "lunchtime", "BOT-TEST", "09:00 AM")
    assert_calendar_items(page, "next", "Week", [{"item_type": "blocked_time", "item_title": "BOT-TEST"}])
