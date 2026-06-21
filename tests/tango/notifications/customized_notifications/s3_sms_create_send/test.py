"""Create and send a customized SMS notification via the v3 API (VCITA2-14248).

Migrated from automation-js/features/tango/customized-email-notification.feature — Scenario 3
("Create and send customized SMS notification").

Distinct scope: the v3 SMS channel — enable SMS in NC settings, send via v3, and assert the
v3 sms notification STATUS ("in_progress").
"""

from playwright.sync_api import Page

from tests import account_api
from tests.tango.notifications.notification_center import notifications_helpers as nc


def _en(value: str) -> list:
    return [{"locale": "en", "value": value}]


def test_s3_sms_create_send(page: Page, context: dict) -> None:
    seq = context["nc"]["seq"]
    code = f"new_auto_notification{seq}s3"
    display = f"Customized SMS Notification {seq}"
    description = "This is a test notification template."
    token = nc.directory_token(context)
    staff_uid = account_api.first_staff_uid(context)

    nc.ensure_owner_session(page, context)

    # ----- API precondition: customized SMS v3 template -----
    nc.create_notification_template_v3(
        context,
        token,
        code_name=code,
        category="payments",
        configurable_by_staff=True,
        title=_en(display),
        description=_en(description),
        content={"sms": {"message_body": _en("SMS Message Body with ${name}")}},
    )

    # ----- 1. Shows in NC settings -----
    nc.goto_settings(page, context)
    nc.assert_template_in_settings(page, code, display_name=display, description=description)
    print("  [OK] v3 sms template shows in NC settings")

    # ----- 2. Staff enables the SMS channel (UI action) + save -----
    nc.set_channel_checkbox(page, code, "sms", checked=True)
    print("  [OK] SMS channel enabled")

    # ----- 3. Send via v3 (passed -> uid) -----
    uid = nc.send_notification_v3(
        context, token, code, staff_uid, params=[{"key": "name", "value": "Business Name"}]
    )
    assert uid, "v3 sms send should have returned a notification uid (passed)"

    # ----- 4. v3 sms status contains "in_progress" -----
    nc.assert_v3_channel_status_contains(context, token, uid, "sms", "in_progress")
    print("  [OK] v3 sms notification status contains 'in_progress'")
