"""Leave a default review, configure Facebook, leave a Facebook review.

Migrates automation-js features/tempo/reviews.feature scenario 1
(Set review settings and invite client to review).
"""

from playwright.sync_api import Page

from tests.tempo.reviews.reviews_cp_ui import (
    assert_default_submitted,
    assert_review_in_conversation,
    assert_social_submitted,
    leave_review,
)
from tests.tempo.reviews.reviews_settings_ui import set_review_platform

DEFAULT_REVIEW_TEXT = "very good"
FACEBOOK_REVIEW_TEXT = "still very good"
PLATFORM = "Facebook"
PLATFORM_ID = "vcitainc"


def test_default_then_facebook_review(page: Page, context: dict) -> None:
    print("  Step 1: Client leaves a default review in the client portal...")
    leave_review(page, context, DEFAULT_REVIEW_TEXT)

    print("  Step 2: Verify the default review submitted page appears...")
    assert_default_submitted(page)
    print("    [OK] default 'Thanks for your review!' page shown")

    print("  Step 3: Verify the default review shows in the conversation...")
    assert_review_in_conversation(page, context, DEFAULT_REVIEW_TEXT)
    print(f"    [OK] conversation shows review '{DEFAULT_REVIEW_TEXT}'")

    print(f"  Step 4: Configure review platform '{PLATFORM}' in back-office settings...")
    set_review_platform(page, context, PLATFORM, PLATFORM_ID)
    print(f"    [OK] platform '{PLATFORM}' saved with id '{PLATFORM_ID}'")

    print("  Step 5: Client leaves a second review (platform configured)...")
    leave_review(page, context, FACEBOOK_REVIEW_TEXT)

    print(f"  Step 6: Verify the '{PLATFORM}' social submitted page appears...")
    assert_social_submitted(page, PLATFORM)
    print(f"    [OK] '{PLATFORM}' social review button shown")

    print("  Step 7: Verify the second review shows in the conversation...")
    assert_review_in_conversation(page, context, FACEBOOK_REVIEW_TEXT)
    print(f"    [OK] conversation shows review '{FACEBOOK_REVIEW_TEXT}'")
