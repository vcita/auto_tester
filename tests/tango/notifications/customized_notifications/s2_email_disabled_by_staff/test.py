"""Customized email notification disabled by staff via the v3 API (VCITA2-14248).

Migrated from automation-js/features/tango/customized-email-notification.feature — Scenario 2
("Customized email notification is disabled by staff").

Staff unchecks the email channel for a v3 template in NC settings; it persists; the v3 send
then fails. Distinct from notification_center (which unchecks the *pane* channel of a v1
template) — here the channel is email and the assertion is on the v3 send being rejected.
"""

from playwright.sync_api import Page

from tests import account_api
from tests.tango.notifications.notification_center import notifications_helpers as nc


def _en(value: str) -> list:
    return [{"locale": "en", "value": value}]


def test_s2_email_disabled_by_staff(page: Page, context: dict) -> None:
    seq = context["nc"]["seq"]
    code = f"new_auto_notification{seq}s2"
    display = f"Customized Email Notification {seq}"
    description = "This is a test notification template."
    token = nc.directory_token(context)
    staff_uid = account_api.first_staff_uid(context)

    nc.ensure_owner_session(page, context)

    # ----- API precondition: customized EMAIL v3 template (no staff_portal) -----
    nc.create_notification_template_v3(
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
            }
        },
    )

    # ----- 1. Shows in NC settings -----
    nc.goto_settings(page, context)
    nc.assert_template_in_settings(page, code, display_name=display, description=description)
    print("  [OK] v3 email template shows in NC settings")

    # ----- 2. Staff unchecks the email channel (UI action) + save -----
    nc.set_channel_checkbox(page, code, "email", checked=False)

    # ----- 3. Refresh -> email channel persists as false -----
    nc.goto_settings(page, context)  # "refresh the page" = re-navigate
    nc.assert_channel_values(page, code, {"email": "false"})
    print("  [OK] Email channel unchecked and persisted (email=false)")

    # ----- 4. Send via v3: the staff-disabled email channel is NOT delivered -----
    # Legacy asserted the SEND failed (null uid on a non-2xx) when the only channel was
    # staff-disabled. On the current backend the send returns 201 but does NOT dispatch the
    # disabled channel (email_status stays null vs ["in_progress"] when enabled). We assert that
    # behavior-equivalent outcome: the email channel was not dispatched (see helper + changelog).
    uid = nc.send_notification_v3(
        context, token, code, staff_uid, params=[{"key": "name", "value": "Business Name"}]
    )
    assert uid, "v3 send unexpectedly returned no notification (current backend returns 201)"
    nc.assert_v3_channel_not_dispatched(context, token, uid, "email")
    print("  [OK] Email channel NOT delivered while disabled by staff")
