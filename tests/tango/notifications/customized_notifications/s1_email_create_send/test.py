"""Create and send a customized EMAIL notification via the v3 API (VCITA2-14248).

Migrated from automation-js/features/tango/customized-email-notification.feature — Scenario 1
("Create and send customized email notification").

Distinct scope vs notification_center (nc_settings/email_settings cover the v1-metadata
channel visibility): this exercises the **v3 communication template** path — create + update
via v3, send via v3, and the v3 sent-notification email STATUS ("processed").
"""

from playwright.sync_api import Page

from tests import account_api
from tests.tango.notifications.notification_center import notifications_helpers as nc


def _en(value: str) -> list:
    return [{"locale": "en", "value": value}]


def test_s1_email_create_send(page: Page, context: dict) -> None:
    seq = context["nc"]["seq"]
    code = f"new_auto_notification{seq}s1"
    display = f"Customized Email Notification {seq}"
    updated_display = f"Customized Email Notification Updated Title {seq}"
    description = "This is a test notification template."
    token = nc.directory_token(context)
    staff_uid = account_api.first_staff_uid(context)

    # Ensure we run as the account owner (independent of prior tests in the subcategory).
    nc.ensure_owner_session(page, context)

    # ----- API precondition: customized EMAIL v3 template -----
    template = nc.create_notification_template_v3(
        context,
        token,
        code_name=code,
        category="payments",
        configurable_by_staff=True,
        title=_en(display),
        description=_en(description),
        content={
            "email": {
                "subject": _en("Email Subject"),
                "main_title": _en("Main Title For ${name}"),
                "main_text": _en("Main Text"),
                "primary_cta_button": {"text": _en("Primary CTA Button")},
            },
            "staff_portal": {
                "title": _en("Hello, ${name}"),
                "message_body": _en("Welcome"),
            },
        },
    )
    template_uid = template["uid"]

    # ----- 1. Shows in NC settings -----
    nc.goto_settings(page, context)
    nc.assert_template_in_settings(page, code, display_name=display, description=description)
    print("  [OK] v3 email template shows in NC settings")

    # ----- 2. Send via v3 (passed -> staff-notification uid) -----
    notif_uid = nc.send_notification_v3(
        context, token, code, staff_uid, params=[{"key": "name", "value": "Business Name"}]
    )
    assert notif_uid, "v3 email send should have returned a notification uid (passed)"

    # ----- 3. New notification created -----
    nc.assert_v3_notification_created(context, token, notif_uid)
    print("  [OK] v3 notification sent and created")

    # ----- 4. Update the TEMPLATE (title + CTA) via v3 (template uid, not the send uid) -----
    nc.update_notification_template_v3(
        context,
        token,
        template_uid,
        {
            "title": _en(updated_display),
            "content": {
                "email": {"primary_cta_button": {"text": _en("Primary CTA Button update name")}}
            },
        },
    )

    # ----- 5. Refresh settings -> updated display -----
    nc.goto_settings(page, context)  # "refresh the page" = re-navigate (no page.reload)
    nc.assert_template_in_settings(
        page, code, display_name=updated_display, description=description
    )
    print("  [OK] Updated title shows in NC settings after refresh")

    # ----- 6. Badge counter "1" -----
    nc.goto_dashboard(page, context)
    nc.assert_badge_counter(page, "1")
    print("  [OK] Notification badge counter is 1")

    # ----- 7. v3 email status contains "processed" -----
    nc.assert_v3_channel_status_contains(context, token, notif_uid, "email", "processed")
    print("  [OK] v3 email notification status contains 'processed'")
