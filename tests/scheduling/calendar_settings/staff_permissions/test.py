# Auto-generated from script.md
# Source: tests/scheduling/calendar_settings/staff_permissions/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

from playwright.sync_api import Page

from tests.scheduling.calendar.calendar_api import create_platform_staff, unique_email
from tests.scheduling.calendar.calendar_helpers import switch_logged_in_staff
from tests.scheduling.calendar_settings.calendar_settings_helpers import (
    open_calendar_settings_page,
    read_settings_side_nav,
)


def test_staff_permissions(page: Page, context: dict) -> None:
    # Step 1: Owner side-nav layout
    open_calendar_settings_page(page)
    owner_layout = read_settings_side_nav(page)
    assert owner_layout == {"has_staff_select": "true", "settings_tabs": "4"}, owner_layout

    # Step 2-3: Create a limited staff member and switch session to them
    staff = create_platform_staff(context, "Staff User", unique_email("staff-u"), "user")
    switch_logged_in_staff(page, context, staff)

    # Step 4 / Verification: limited-staff side-nav layout
    open_calendar_settings_page(page)
    staff_layout = read_settings_side_nav(page)
    assert staff_layout == {"has_staff_select": "false", "settings_tabs": "3"}, staff_layout
