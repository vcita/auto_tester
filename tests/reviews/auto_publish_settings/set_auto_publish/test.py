"""Set review auto-publish settings when the directory has an external review site.

Migrates automation-js features/tempo/reviews.feature scenario 3
(Set review auto-publish settings).
"""

from playwright.sync_api import Page

from tests.reviews.auto_publish_settings.directory_setup import activate_business, fresh_login
from tests.reviews.reviews_cp_ui import assert_cp_auto_publish_visibility
from tests.reviews.reviews_settings_ui import (
    assert_auto_publish_checked_and_label,
    set_review_platform,
    toggle_auto_publish_and_save,
)

PLATFORM = "Facebook"
PLATFORM_ID = "vcitainc"
REVIEW_SITE_NAME = "vcita"


def test_set_auto_publish(page: Page, context: dict) -> None:
    triple = activate_business(context, "auto_publish_with_site")

    print("  Step 1: Log in as the in-directory business (review site: vcita)...")
    fresh_login(page, context, username=triple["email"], password=triple["password"])

    print(f"  Step 2: Select review platform '{PLATFORM}' with id '{PLATFORM_ID}'...")
    set_review_platform(page, context, PLATFORM, PLATFORM_ID)
    print("    [OK] platform saved")

    print("  Step 3: Toggle the auto-publish checkbox on and save...")
    toggle_auto_publish_and_save(page, context)
    print("    [OK] auto-publish enabled and saved")

    print(f"  Step 4: Verify auto-publish is checked and labelled '{REVIEW_SITE_NAME}'...")
    assert_auto_publish_checked_and_label(page, context, REVIEW_SITE_NAME)
    print("    [OK] auto-publish checked with review site name")

    print("  Step 5: Verify the client-portal review page shows the auto-publish checkbox...")
    assert_cp_auto_publish_visibility(page, context, should_display=True)
    print("    [OK] client-portal auto-publish checkbox displayed")
