# Auto-generated from script.md
# Source: tests/scheduling/calendar_settings/business_settings/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

from playwright.sync_api import Page

from tests.tempo.scheduling.appointments.appointment_helpers import open_calendar_page
from tests.tempo.scheduling.calendar_settings.calendar_settings_helpers import (
    get_calendar_week_display,
    hide_weekends,
    set_business_settings,
)


def test_business_settings(page: Page, context: dict) -> None:
    # Step 1: Open the Calendar page
    open_calendar_page(page)

    # Step 2-5: Set business settings (start-of-week + time format), save, close
    set_business_settings(page, week_start_day="Tuesday", time_format="24 hours")

    # Step 6: Switch to Week view and hide weekends
    hide_weekends(page)

    # Verification: Week-view header
    display = get_calendar_week_display(page)
    assert display == {"week_start_day": "Tue", "time_format": "00:00", "num_of_days": "5"}, display
