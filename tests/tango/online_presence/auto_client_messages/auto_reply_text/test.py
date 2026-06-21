"""Auto reply text change (VCITA2-14249).

Migrated from automation-js/features/tango/auto-client-messages.feature
(Scenario: "auto reply text change").

A business updates the auto-reply message text in settings. When a client leaves
their details via the public livesite contact form, the livesite success page
displays the updated auto-reply message — proving the settings change took effect
end-to-end.
"""

import time

from playwright.sync_api import Page

from tests.tango.online_presence.auto_client_messages.auto_client_messages_helpers import (
    assert_success_message,
    leave_details_on_livesite,
    update_auto_reply,
)

AUTO_REPLY_TEXT = "bla2"


def test_auto_reply_text(page: Page, context: dict) -> None:
    seq = int(time.time())
    details = {
        "subject": "hi",
        "message": "hello",
        "email": f"form+{seq}@vmeetme.com",
        "first_name": "form_first",
        "last_name": "form_last",
    }

    # Step 1: Update the auto-reply message text in settings.
    update_auto_reply(page, context, AUTO_REPLY_TEXT)
    print(f"  [OK] Updated auto-reply message to '{AUTO_REPLY_TEXT}'")

    # Step 2: As a public visitor, leave details on the livesite contact form.
    leave_details_on_livesite(page, context, details)
    print("  [OK] Submitted leave-details form on the livesite")

    # Step 3: The livesite success page displays the configured auto-reply message.
    assert_success_message(page, AUTO_REPLY_TEXT)
    print(f"  [OK] Success page displays auto message '{AUTO_REPLY_TEXT}'")
