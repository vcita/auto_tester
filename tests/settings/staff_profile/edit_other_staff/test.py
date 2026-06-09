"""Admin edits another staff's profile (VCITA2-14004, scenario 2).

Migrates automation-js staff-profile-page.feature "Admin opens other staff
profile page and updates data". The second staff is created in setup; the
password field must NOT be shown for another staff, and the email stays unchanged.
"""

from playwright.sync_api import Page

from tests.settings.staff_profile.staff_profile_helpers import (
    assert_profile,
    open_staff_profile,
    open_staff_settings_landing,
    settings_tiles_count,
    update_profile,
)

UPDATE = {
    "country_code": "CA",
    "display_name": "User Staff Modified",
    "first_name": "User",
    "last_name": "Staff_Modified",
    "mobile_number": "0525555555",
    "professional_title": "Lead User",
    "default_homepage": "Inbox",
}


def test_edit_other_staff(page: Page, context: dict) -> None:
    staff = context["staff_profile"]["user_staff"]
    print(f"  Editing staff {staff['name']!r} ({staff['email']}) uid={staff['uid']}")

    open_staff_settings_landing(page, staff["name"])
    tiles = settings_tiles_count(page)
    assert tiles == 3, f"expected 3 settings tiles for the staff, got {tiles}"
    print(f"  [OK] Staff settings landing shows {tiles} tiles")

    open_staff_profile(page, staff["uid"])
    assert_profile(
        page,
        {
            "display_name": "user_staff",
            "email": staff["email"],
            "default_homepage": "Dashboard",
        },
    )
    print("  [OK] Staff profile shows display name/email/Dashboard homepage")

    update_profile(page, UPDATE)

    open_staff_profile(page, staff["uid"])
    assert_profile(
        page,
        {
            "display_name": "User Staff Modified",
            "first_name": "User",
            "last_name": "Staff_Modified",
            "mobile_number": "0525555555",
            "professional_title": "Lead User",
            "default_homepage": "Inbox",
            "country_name": "Canada",
            "email": staff["email"],
            "password_field": "not displayed",
        },
    )
    print("  [OK] Updated staff profile persisted (fields, Canada, Inbox, email unchanged, no password)")
