"""Auto-publish settings hidden when the directory has no external review site.

Migrates automation-js features/tempo/reviews.feature scenario 2
(Auto-publish settings does not appear in review settings page).
"""

from playwright.sync_api import Page

from tests.reviews.auto_publish_settings.directory_setup import activate_business, fresh_login
from tests.reviews.reviews_cp_ui import assert_cp_auto_publish_visibility
from tests.reviews.reviews_settings_ui import assert_auto_publish_section_absent


def test_auto_publish_hidden(page: Page, context: dict) -> None:
    triple = activate_business(context, "auto_publish_no_site")

    print("  Step 1: Log in as the in-directory business (no external review site)...")
    fresh_login(page, context, username=triple["email"], password=triple["password"])

    print("  Step 2: Verify the reviews settings auto-publish checkbox is NOT displayed...")
    assert_auto_publish_section_absent(page, context)
    print("    [OK] back-office auto-publish section absent (page rendered)")

    print("  Step 3: Verify the client-portal review page auto-publish checkbox is NOT displayed...")
    assert_cp_auto_publish_visibility(page, context, should_display=False)
    print("    [OK] client-portal auto-publish checkbox absent")
