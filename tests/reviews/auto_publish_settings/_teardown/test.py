"""Teardown for the reviews auto_publish_settings subcategory.

Best-effort cleanup of the two in-directory businesses created in setup (the
isolated runner account is cleaned up by the runner; the directories themselves are
left in place, matching the legacy scenarios which did not delete them).
"""

from playwright.sync_api import Page

from tests.reviews.auto_publish_settings.directory_setup import delete_business


def teardown_auto_publish_settings(page: Page, context: dict) -> None:
    for key in ("auto_publish_no_site", "auto_publish_with_site"):
        triple = context.get(key)
        if triple and triple.get("business_uid"):
            delete_business(context, triple["business_uid"])
            print(f"  [teardown] Deleted business {triple['email']}")
