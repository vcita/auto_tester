"""Admin edits own staff profile (VCITA2-14004, scenario 1).

Migrates automation-js staff-profile-page.feature "Admin opens own staff profile
page and updates data". The account display name is dynamic, so the initial
display-name expectation is read from the API in setup (context owner).
"""

from playwright.sync_api import Page

from tests.settings.staff_profile.staff_profile_helpers import (
    assert_profile,
    open_own_profile,
    update_profile,
)

UPDATE = {
    "country_code": "AL",
    "display_name": "Admin Staff Updated",
    "first_name": "Admin",
    "last_name": "Staff_Updated",
    "mobile_number": "0528888888",
    "professional_title": "Senior Administrator",
    "default_homepage": "Calendar",
}


def test_edit_own_profile(page: Page, context: dict) -> None:
    owner = context["staff_profile"]["owner"]
    print(f"  Owner display name (initial expected): {owner['display_name']!r}")

    open_own_profile(page)
    assert_profile(page, {"display_name": owner["display_name"], "default_homepage": "Dashboard"})
    print("  [OK] Initial own profile shows account display name + Dashboard homepage")

    update_profile(page, UPDATE)

    open_own_profile(page)
    assert_profile(
        page,
        {
            "display_name": "Admin Staff Updated",
            "first_name": "Admin",
            "last_name": "Staff_Updated",
            "mobile_number": "0528888888",
            "professional_title": "Senior Administrator",
            "default_homepage": "Calendar",
            "country_name": "Albania",
            "password_field": "displayed",
        },
    )
    print("  [OK] Updated own profile persisted (fields, Albania, Calendar, password displayed)")
